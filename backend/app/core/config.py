from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # =====================================================
    # DATABASE
    # =====================================================

    DATABASE_URL: str

    # =====================================================
    # JWT
    # =====================================================

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # =====================================================
    # WHATSAPP CLOUD API
    # =====================================================

    WHATSAPP_ENABLED: bool = False

    WHATSAPP_ACCESS_TOKEN: str = ""

    WHATSAPP_PHONE_NUMBER_ID: str = ""

    WHATSAPP_GRAPH_VERSION: str = "v25.0"

    WHATSAPP_TEMPLATE_NAME: str = "new_service_request"

    WHATSAPP_TEMPLATE_LANGUAGE: str = "en_US"

    # =====================================================
    # OPTIONAL NOTIFICATION NUMBERS
    # =====================================================

    WHATSAPP_NOTIFICATION_NUMBERS: str = ""

    # =====================================================
    # PYDANTIC SETTINGS
    # =====================================================

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()