import jwt
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import uuid
from sqlmodel import select

from config import Config
from database.ext_db import Session
from models.sql import User, UserRole, LawFirm
from models.api.user import UserCreate


class UserAuthService:
    SECRET_KEY = Config.JWT_SECRET_KEY
    ALGORITHM = Config.JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    @classmethod
    def create_user(cls, session: Session, user_data: UserCreate) -> User:
        """Create a new user in the database."""
        # Check if user already exists
        existing_user = session.exec(
            select(User).where(User.name == user_data.name)
        ).first()
        
        if existing_user:
            raise ValueError("User with this name already exists")
        
        # Validate law_firm_id if provided
        if user_data.law_firm_id:
            law_firm = session.exec(
                select(LawFirm).where(LawFirm.id == user_data.law_firm_id)
            ).first()
            
            if not law_firm:
                raise ValueError("Law firm not found")
        
        # Create new user
        user = User(
            name=user_data.name,
            role=user_data.role,
            active=True,
            law_firm_id=user_data.law_firm_id
        )
        user.set_password(user_data.password)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @classmethod
    def authenticate_user(cls, session: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = session.exec(
            select(User).where(User.name == username)
        ).first()
        
        if not user:
            return None
        
        if not user.verify_password(password):
            return None
        
        if not user.active:
            return None
        
        return user
    
    @classmethod
    def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        
        now = datetime.utcnow()
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": now,                    # ⬅ issued at
            "jti": str(uuid.uuid4()),      # ⬅ identificador único
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            cls.SECRET_KEY,
            algorithm=cls.ALGORITHM
        )
        
        return encoded_jwt
    
    @classmethod
    def verify_token(cls, token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    @classmethod
    def get_current_user(cls, session: Session, token: str) -> Optional[User]:
        """Get current user from token."""
        payload = cls.verify_token(token)
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        try:
            user_uuid = UUID(user_id)
            user = session.exec(
                select(User).where(User.id == user_uuid)
            ).first()
            
            if user is None or not user.active:
                return None
            
            return user
        except ValueError:
            return None
    
    @classmethod
    def get_user_by_id(cls, session: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return session.exec(
            select(User).where(User.id == user_id)
        ).first()
    
    @classmethod
    def update_user_role(cls, session: Session, user_id: UUID, new_role: UserRole) -> Optional[User]:
        """Update user role."""
        user = cls.get_user_by_id(session, user_id)
        if not user:
            return None
        
        user.role = new_role
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @classmethod
    def deactivate_user(cls, session: Session, user_id: UUID) -> bool:
        """Deactivate a user."""
        user = cls.get_user_by_id(session, user_id)
        if not user:
            return False
        
        user.active = False
        session.add(user)
        session.commit()
        
        return True 