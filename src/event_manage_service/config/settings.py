from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Event Manage Service"
    version: str = "0.1.0"
    description: str = ""
    debug: bool = False
    host: str = "localhost"
    port: int = 8001
    env: str = "DEV"
    
    # Database settings
    database_url: str = "mysql+aiomysql://backend:Backend123!@158.247.220.157:3306/event_manage_db"
    
    class Config:
        env_file = ".env"


settings = Settings()