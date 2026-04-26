from uuid import UUID

from app.modules.users.domain.user import User, UserCreate, UserRole
from app.modules.users.infrastructure.models import UserModel

def user_model_to_domain(model: UserModel) -> User:
    return User(
        id=UUID(model.id),
        username=model.username,
        display_name=model.display_name,
        bio=model.bio,
        avatar_image=model.avatar_image,
        password_hash=model.password_hash,
        ldap=model.ldap,
        role=UserRole(model.role),
        is_active=model.is_active,
        last_seen_version=model.last_seen_version,
        last_login_at=model.last_login_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )

def user_create_to_model(user: UserCreate) -> UserModel:
    return UserModel(
        username=user.username,
        display_name=user.display_name,
        bio=user.bio,
        avatar_image=user.avatar_image,
        password_hash=user.password_hash,
        ldap=user.ldap,
        role=user.role.value,
    )

