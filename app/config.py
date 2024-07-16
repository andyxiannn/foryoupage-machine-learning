from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str
    API_KEY: str

    CLIENT_ORIGIN: str

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: EmailStr
    
    CRONJOB_STATUS: str
    POPULARITY_CRONJOB_INTERVAL: int
    FYP_CRONJOB_INTERVAL: int
    POPULARITY_AMOUNT: int
    FYP_AMOUNT: int

    class Config:
        env_file = './.env'


settings = Settings()
