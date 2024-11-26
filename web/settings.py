from pydantic_settings import BaseSettings
from typing import Optional

class APISettings(BaseSettings):
    max_wait_time_count: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    # MySQL配置
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_database: str = "pytrader"

    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6380
    redis_db: int = 0
    redis_password: Optional[str] = None

    # JWT配置
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API配置
    api_v1_str: str = "/api/v1"
    project_name: str = "PyTrader"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

# 创建设置实例
settings = APISettings()