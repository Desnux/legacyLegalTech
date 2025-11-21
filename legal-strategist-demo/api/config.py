import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    PORT = os.getenv("STRATEGIST_PORT", "8100")
    RESPOND_EMAIL_WEBHOOK_URL = os.getenv("RESPOND_EMAIL_WEBHOOK_URL", "")
    SEND_EMAIL_WEBHOOK_URL = os.getenv("SEND_EMAIL_WEBHOOK_URL", "")
    ASSISTANT_EMAIL = os.getenv("ASSISTANT_EMAIL", "asistencia@titangroup.la")
    EMAIL_BLACKLIST = os.getenv("EMAIL_BLACKLIST", "")
    EMAIL_WHITELIST = os.getenv("EMAIL_WHITELIST", "titangroup.la")
    DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "titangroup123456")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_DATABASE = os.getenv("DB_DATABASE", "titangroup")
    DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    AWS_REGION = os.getenv("AWS_REGION", "")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    S3_BUCKET = os.getenv("S3_BUCKET", "")
    TWO_CAPTCHA_KEY = os.getenv("TWO_CAPTCHA_KEY", "")
    MAX_FILE_SIZE_MB = 4
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    MAX_BATCH_FILE_SIZE_MB = 10
    MAX_BATCH_FILE_SIZE_BYTES = MAX_BATCH_FILE_SIZE_MB * 1024 * 1024

    @classmethod
    def validate_openai_api_key(cls):
        if len(cls.OPENAI_API_KEY) < 10:
            raise ValueError(f"Invalid OpenAI API key: {cls.OPENAI_API_KEY}")

    @classmethod
    def validate_port(cls):
        try:
            port = int(cls.PORT)
            if 0 <= port <= 65535:
                return True
            raise ValueError(f"Invalid port: {cls.PORT}")
        except ValueError:
            raise ValueError(f"Invalid port: {cls.PORT}")


Config.validate_openai_api_key()
Config.validate_port()