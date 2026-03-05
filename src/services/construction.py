import grpc
import logging
from google.protobuf import timestamp_pb2

# 导入生成的代码
from agent.v1.constructionprogress import construction_pb2
from agent.v1.constructionprogress import construction_pb2_grpc
from src.core.database.database import session_scope
import src.crud.construction_progress

class ConstructionServer(construction_pb2_grpc.ConstructionServiceServicer):
    """实现 ConstructionService 的所有 RPC 方法"""

    def __init__(self):
        self.crud = src.crud.construction_progress.construction_progress_crud

    def CreateConstructionProgress(self, request: construction_pb2.CreateConstructionProgressRequest,
                                   context: grpc.ServicerContext) -> construction_pb2.CreateConstructionProgressResponse:
        """创建项目进度计划"""
        
        with session_scope() as session:
            # 直接组装入库数据，设定默认初始进度
            data = {
                "name": request.name,
                "type": str(request.plan_type),
                "creator": request.creator,
                "progress": str(construction_pb2.ProgressStatus.PROGRESS_STATUS_EXTRACTING)
            }
            
            db_obj = self.crud.create(session, obj_in=data)
            
            res = construction_pb2.CreateConstructionProgressResponse(id=str(db_obj.id))
            if db_obj.created_at:
                res.created_at.FromDatetime(db_obj.created_at)
            res.status = construction_pb2.ProgressStatus.PROGRESS_STATUS_EXTRACTING
            
            return res

    def ListConstruction(self, request: construction_pb2.ListConstructionRequest,
                        context: grpc.ServicerContext) -> construction_pb2.ListConstructionResponse:
        """获取施工进度计划列表"""
        logging.info(f"收到 ListConstruction 请求: page={request.page}, size={request.page_size}")
        
        page = max(request.page, 1)
        page_size = max(request.page_size, 1) if request.page_size > 0 else 10

        with session_scope() as session:
            items = self.crud.list_by_page(session, page=page, page_size=page_size)
            total = session.query(self.crud.model).count()
            
            proto_items = []
            for item in items:
                created_at = None
                if item.created_at:
                    created_at = timestamp_pb2.Timestamp()
                    created_at.FromDatetime(item.created_at)

                # 映射计算逻辑
                try:
                    plan_type = int(item.type)
                except (ValueError, TypeError):
                    plan_type = 0
                
                try:
                    status = int(item.progress)
                except (ValueError, TypeError):
                    status = 1 

                proto_items.append(construction_pb2.ConstructionProgress(
                    id=str(item.id),
                    name=item.name,
                    plan_type=plan_type,
                    status=status,
                    creator=item.creator,
                    created_at=created_at
                ))
            
            return construction_pb2.ListConstructionResponse(
                items=proto_items,
                total=total,
                page=page,
                page_size=page_size
            )

    def DeleteConstructionProgress(self, request: construction_pb2.DeleteConstructionProgressRequest,
                                   context: grpc.ServicerContext) -> construction_pb2.DeleteConstructionProgressResponse:
        """删除项目进度计划"""
        logging.info(f"收到 DeleteConstructionProgress 请求: id={request.id}")
        
        with session_scope() as session:
            item_id = int(request.id) if request.id.isdigit() else request.id
            db_obj = self.crud.remove(session, id=item_id)
            if not db_obj:
                return construction_pb2.DeleteConstructionProgressResponse(
                    success=False, message="未找到该进度计划"
                )
            return construction_pb2.DeleteConstructionProgressResponse(success=True)
