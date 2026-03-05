from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .pgsql import db_config

# 创建基类
Base = declarative_base()

# 创建数据库引擎
DATABASE_URL = db_config.get_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=True,  # 显示 SQL 语句（调试用，生产环境设为 False）
    pool_size=5,  # 连接池大小
    max_overflow=10,  # 最大溢出连接数
    pool_pre_ping=True,  # 连接前检查连接是否有效
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")


from contextlib import contextmanager

@contextmanager
def session_scope():
    """提供一个事务范围的会话上下文管理器。
    
    用法:
        with session_scope() as session:
            crud.create(session, obj)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db():
    """获取数据库会话（FastAPI/依赖注入方式用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()