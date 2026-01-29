import grpc
from concurrent import futures
import logging
import signal
import sys

from src.services.construction import ConstructionServer
from src.services.interceptors import ErrorHandlingInterceptor
from agent.v1.constructionprogress import construction_pb2_grpc

def serve():
    """启动 gRPC 服务器"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 配置 gRPC Keepalive 选项，彻底解决 "too_many_pings" (ENHANCE_YOUR_CALM) 错误
    server_options = [
        # 允许客户端在无活跃 RPC 时发送 Keepalive 探测
        ('grpc.keepalive_permit_without_calls', 1),
        # 服务器允许的客户端最小探测间隔（设置得足够小以包容客户端的 30s 频率）
        ('grpc.http2.min_ping_interval_without_data_ms', 5000),
        # 禁用惩罚机制，即使探测过快也不断开连接
        ('grpc.http2.max_ping_strikes', 0),
        # 允许在没有数据传输时发送无限次心跳
        ('grpc.http2.max_pings_without_data', 0),
        # 服务器主动探测客户端的频率
        ('grpc.keepalive_time_ms', 120000),             # 2 分钟
        ('grpc.keepalive_timeout_ms', 20000),           # 20 秒超时
    ]

    # 创建服务器，应用全局异常拦截器
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[ErrorHandlingInterceptor()],
        options=server_options
    )

    # 注册服务实现
    construction_pb2_grpc.add_ConstructionServiceServicer_to_server(
        ConstructionServer(), server
    )

    # 监听端口
    port = 50051
    server.add_insecure_port(f'0.0.0.0:{port}')

    # 优雅关闭处理
    def shutdown(signum, frame):
        logging.info("收到关闭信号，优雅停止服务器...")
        server.stop(5)  # 5秒超时
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # 启动服务器
    server.start()
    logging.info(f"gRPC 服务器启动，监听端口: {port}")

    # 保持运行
    server.wait_for_termination()

if __name__ == '__main__':
    serve()