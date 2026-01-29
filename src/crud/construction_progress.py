from sqlalchemy.orm import Session
from typing import Optional, Union, Dict, Any, Type, List
from src.crud.base import CRUDBase
from src.models.construction_progress import ConstructionProgress

class ConstructionProgressCRUD(CRUDBase[ConstructionProgress, Any, Any]):
    """施工进度 CRUD 实现，继承自 CRUDBase 以利用通用方法。"""
    
    def list_by_page(self, db: Session, *, page: int = 1, page_size: int = 10) -> List[ConstructionProgress]:
        skip = (page - 1) * page_size
        return self.get_multi(db, skip=skip, limit=page_size)

    def close(self):
        # 保持接口兼容，但在新的 session_scope 模式下通常不直接调用此方法
        pass

construction_progress_crud = ConstructionProgressCRUD(ConstructionProgress)