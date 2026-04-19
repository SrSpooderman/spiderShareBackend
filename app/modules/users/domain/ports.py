from abc import ABC, abstractmethod
from uuid import UUID
from app.modules.users.domain.user import User, UserCreate


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_uuid: UUID) -> User | None:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    def create(self, user: UserCreate) -> User:
        pass
