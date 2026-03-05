import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """数据库配置类"""

    # PostgreSQL 配置（生产环境）
    POSTGRES_HOST: Optional[str] = os.getenv("DB_HOST", "localhost")
    POSTGRES_PORT: Optional[str] = os.getenv("DB_PORT", "5432")
    POSTGRES_DB: Optional[str] = os.getenv("DB_NAME", "mydatabase")
    POSTGRES_USER: Optional[str] = os.getenv("DB_USER", "postgres")
    POSTGRES_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD", "your_strong_password_here")

    @property
    def postgres_url(self) -> str:
        """PostgreSQL 数据库 URL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def get_database_url(self) -> str:
        """获取数据库连接 URL"""
        return self.postgres_url


# 配置实例
db_config = DatabaseConfig()