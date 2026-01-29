package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/grpc-ecosystem/grpc-gateway/v2/runtime"
	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/keepalive"

	// 导入生成的代码
	pb "gitlab.bjuci.io/agent-be/proto/agent/v1/constructionprogress"
)

const (
	defaultGrpcServerAddr = "127.0.0.1:50051" // Python gRPC服务默认地址
	defaultGatewayAddr    = ":8080"           // HTTP网关默认监听地址
)

func main() {
	// 从环境变量读取配置
	grpcServerAddr := os.Getenv("GRPC_SERVER_ADDR")
	if grpcServerAddr == "" {
		grpcServerAddr = defaultGrpcServerAddr
	}
	gatewayAddr := os.Getenv("GATEWAY_ADDR")
	if gatewayAddr == "" {
		gatewayAddr = defaultGatewayAddr
	}

	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)
	defer cancel()

	// 1. 创建gRPC客户连接（推荐使用 NewClient，Go 1.21+）
	grpcConn, err := grpc.NewClient(
		grpcServerAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithKeepaliveParams(keepalive.ClientParameters{
			Time:                30 * time.Second,
			Timeout:             10 * time.Second,
			PermitWithoutStream: true,
		}),
		grpc.WithDefaultCallOptions(
			grpc.MaxCallRecvMsgSize(1024*1024*10), // 10MB
			grpc.MaxCallSendMsgSize(1024*1024*10), // 10MB
		),
	)
	if err != nil {
		log.Fatalf("创建gRPC客户端失败: %v", err)
	}
	defer func() {
		log.Println("正在关闭 gRPC 连接...")
		if err := grpcConn.Close(); err != nil {
			log.Printf("关闭 gRPC 连接失败: %v", err)
		}
	}()

	log.Printf("gRPC 客户端已就绪，目标地址: %s", grpcServerAddr)

	// 2. 创建gRPC网关Mux
	gwMux := runtime.NewServeMux(
		runtime.WithMarshalerOption(runtime.MIMEWildcard, &runtime.JSONPb{
			MarshalOptions:   runtime.JSONPb{}.MarshalOptions,
			UnmarshalOptions: runtime.JSONPb{}.UnmarshalOptions,
		}),
		runtime.WithErrorHandler(runtime.DefaultHTTPErrorHandler),
	)

	// 3. 注册HTTP处理器
	err = pb.RegisterConstructionServiceHandler(ctx, gwMux, grpcConn)
	if err != nil {
		log.Fatalf("注册HTTP处理器失败: %v", err)
	}

	// 4. 创建HTTP服务器
	mux := http.NewServeMux()

	// 健康检查
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"status":"ok","service":"grpc-gateway","timestamp":"%s"}`,
			time.Now().Format(time.RFC3339))
	})

	// 注册gRPC网关路由
	mux.Handle("/", gwMux)

	// 5. 配置HTTP服务器
	server := &http.Server{
		Addr:         gatewayAddr,
		Handler:      h2c.NewHandler(mux, &http2.Server{}), // 支持基础 HTTP/2 (h2c)
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// 6. 优雅关闭
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("服务器启动失败: %v", err)
		}
	}()

	log.Printf("gRPC网关已启动，监听地址: %s", gatewayAddr)
	log.Printf("健康检查: http://localhost%s/health", gatewayAddr)

	// 等待信号
	<-stop
	log.Println("收到关闭信号，正在优雅停止服务器...")

	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownCancel()

	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Printf("服务器优雅关闭失败: %v", err)
	}

	log.Println("服务器已正常退出")
}
