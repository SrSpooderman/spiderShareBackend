from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.domain.ports import UserRepository
from app.modules.users.domain.user import User, UserCreate
from app.modules.users.infrastructure.mappers import (
    user_create_to_model,
    user_model_to_domain,
)
from app.modules.users.infrastructure.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_uuid: UUID) -> User | None:
        statement = select(UserModel).where(UserModel.id == str(user_uuid))
        model = self.session.scalar(statement)

        if model is None:
            return None

        return user_model_to_domain(model)

    def get_by_username(self, username: str) -> User | None:
        statement = select(UserModel).where(UserModel.username == username)
        model = self.session.scalar(statement)

        if model is None:
            return None

        return user_model_to_domain(model)

    def create(self, user: UserCreate) -> User:
        model = user_create_to_model(user)

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        return user_model_to_domain(model)
