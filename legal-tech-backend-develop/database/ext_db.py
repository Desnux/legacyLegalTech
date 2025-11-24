from typing import Any, Generator

from sqlmodel import SQLModel, create_engine, Session

import models.sql
from config import Config


engine = create_engine(Config.DATABASE_URL, echo=False)


def init_db() -> None:
    """Initialize the database and create tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, Any, None]:
    """Dependency to provide a session."""
    with Session(engine) as session:
        yield session
