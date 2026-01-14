import grpc
import logging
import src.crud.construction_progress
# 导入生成的代码
from agent.v1.constructionprogress import construction_pb2
from agent.v1.constructionprogress import construction_pb2_grpc
from src.models.construction_progress import ConstructionProgress
from config.database import SessionLocal

class ConstructionServer(construction_pb2_grpc.ConstructionServiceServicer):
    """实现 ExampleService 的所有 RPC 方法"""

    def __init__(self):
        self.DB = SessionLocal
        self.crud = src.crud.construction_progress.construction_progress_crud

    def ListConstruction(self, request: construction_pb2.ListConstructionRequest,
                 context: grpc.ServicerContext) -> construction_pb2.ListConstructionResponse:
        """一元 RPC（客户端请求 → 服务器响应）"""
        logging.info(f"收到 ListConstruction 请求: nums={request.page}")

        # 实现业务逻辑
        # greeting = f"Hello, {request.name}!"

        # 返回响应
        return construction_pb2.ListConstructionResponse(page=request.page)

    def CreateConstructionProgress(self, request: construction_pb2.ConstructionProgress,
                                   context: grpc.ServicerContext) -> construction_pb2.CommonResponse:
        # 每次 RPC 获取独立的 DB session
        session = None
        try:
            # 使用 __init__ 中保存的 DB 工厂/实例
            session = self.DB() if callable(self.DB) else self.DB
            if session is None:
                raise RuntimeError("数据库会话不可用")

            # 构造 ORM 实例
            obj = ConstructionProgress(
                name=request.name,
                type=request.type,
                progress=request.progress,
                creator=request.creator,
            )

            # 优先使用 crud.create（如果存在且返回 ORM 实例），否则直接用 session 操作
            response = self.crud.create(session, obj)
            # 确保提交，发生异常时回滚并抛出
            try:
                session.commit()
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
                raise
            obj_id = getattr(response, "id", None) or getattr(obj, "id", None)
            return construction_pb2.CommonResponse(id=obj_id)

        except Exception as e:
            # 发生异常时回滚并记录
            try:
                if session is not None:
                    session.rollback()
            except Exception:
                pass
            logging.exception("创建 ConstructionProgress 失败")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return construction_pb2.CommonResponse()
        finally:
            try:
                if session is not None:
                    session.close()
            except Exception:
                pass
