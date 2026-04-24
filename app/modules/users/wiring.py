from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.users.domain.ports import UserRepository
from app.modules.users.infrastructure.repository import SqlAlchemyUserRepository
from app.shared.infrastructure.db.session import get_db


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return SqlAlchemyUserRepository(db)
