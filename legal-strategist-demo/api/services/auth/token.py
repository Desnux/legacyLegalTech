from config import Config


class TokenService:
    @classmethod
    def validate_token(cls, user_token: str) -> bool:
        return user_token == Config.AUTH_TOKEN
