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
	grpcServerAddr = "localhost:50051" // Python gRPC服务地址
	gatewayAddr    = ":8080"           // HTTP网关监听地址
)

func main() {
	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)
	defer cancel()

	// 1. 创建gRPC连接（连接到Python服务）
	grpcConn, err := grpc.DialContext(
		ctx,
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
		log.Fatalf("连接gRPC服务失败: %v", err)
	}
	defer grpcConn.Close()

	log.Printf("已连接到gRPC服务: %s", grpcServerAddr)

	// 2. 创建gRPC网关Mux
	gwMux := runtime.NewServeMux(
		// 自定义选项
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
		Handler:      h2c.NewHandler(mux, &http2.Server{}), // 支持HTTP/2
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// 6. 优雅关闭
	go func() {
		sigChan := make(chan os.Signal, 1)
		signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
		<-sigChan

		log.Println("收到关闭信号，正在停止服务器...")
		cancel()

		shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer shutdownCancel()

		if err := server.Shutdown(shutdownCtx); err != nil {
			log.Printf("服务器关闭失败: %v", err)
		}
	}()

	// 7. 启动服务器
	log.Printf("gRPC网关启动，监听地址: %s", gatewayAddr)
	log.Printf("健康检查: http://localhost%s/health", gatewayAddr)

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("服务器启动失败: %v", err)
	}

	log.Println("服务器已停止")
}
