from config import Config
from models.sql import UserGroup


class TokenService:
    @classmethod
    def get_role(cls, user_token: str) -> UserGroup | None:
        match user_token:
            case Config.AUTH_TOKEN:
                return UserGroup.EXECUTIVE_CASE
            case Config.IN_HOUSE_SUITE_TOKEN:
                return UserGroup.IN_HOUSE_SUITE
        return None

    @classmethod
    def validate_token(cls, user_token: str) -> bool:
        return user_token in [Config.AUTH_TOKEN, Config.IN_HOUSE_SUITE_TOKEN]
