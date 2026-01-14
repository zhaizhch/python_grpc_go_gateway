import grpc
from concurrent import futures
import logging
import signal
import sys

from construction import ConstructionServer
from agent.v1.constructionprogress import construction_pb2_grpc

def serve():
    """启动 gRPC 服务器"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建服务器
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        # 可选：添加拦截器
        interceptors=[]
    )

    # 注册服务实现
    construction_pb2_grpc.add_ConstructionServiceServicer_to_server(
        ConstructionServer(), server
    )

    # 监听端口
    port = 50051
    server.add_insecure_port(f'[::]:{port}')

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