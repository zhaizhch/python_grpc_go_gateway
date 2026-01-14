from sqlalchemy.orm import Session
from typing import Optional, Union, Dict, Any, Type, List
from src.crud.base import CRUDBase
from src.models.construction_progress import ConstructionProgress

class ConstructionProgressCRUD:
    def __init__(self, model: Type[ConstructionProgress]):
        self.model = model
        self.session = Session()

    def get(self, db: Session, id: int) -> Optional[ConstructionProgress]:
        return db.query(self.model).filter(self.model.id == id).first()

    def list(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[type[ConstructionProgress]]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: Union[ConstructionProgress, Dict[str, Any]]) -> ConstructionProgress:
        # 支持 pydantic v2 (.model_dump)、pydantic v1 (.dict)、dict 或 SQLAlchemy 实例
        if isinstance(obj_in, dict):
            obj_in_data = obj_in.copy()
        elif hasattr(obj_in, "model_dump"):
            obj_in_data = obj_in.model_dump()
        elif hasattr(obj_in, "dict"):
            obj_in_data = obj_in.dict()
        else:
            # 从 SQLAlchemy 实例提取字段，排除内部属性（例如 _sa_instance_state）
            obj_in_data = {
                k: v
                for k, v in getattr(obj_in, "__dict__", {}).items()
                if not k.startswith("_") and k != "_sa_instance_state"
            }
        obj_in_data.pop("id", None)

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            *,
            db_obj: ConstructionProgress,
            obj_in: Union[ConstructionProgress, Dict[str, Any]]
    ) -> ConstructionProgress:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ConstructionProgress:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def close(self):
        self.session.close()

construction_progress_crud = ConstructionProgressCRUD(ConstructionProgress)