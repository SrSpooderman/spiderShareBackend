from sqlalchemy import select

from app.modules.auth.application.password_hasher import PasswordHasher
from app.modules.users.domain.user import UserRole
from app.modules.users.infrastructure.models import UserModel
from app.shared.infrastructure.db.session import SessionLocal
from config.settings import settings


def seed_super_admin() -> None:
    username = settings.super_admin_username
    password = settings.super_admin_password

    if not username and not password:
        print("SUPER_ADMIN_USERNAME and SUPER_ADMIN_PASSWORD not configured. Skipping seed.")
        return

    if not username or not password:
        raise RuntimeError(
            "Both SUPER_ADMIN_USERNAME and SUPER_ADMIN_PASSWORD must be configured.",
        )

    with SessionLocal() as session:
        existing_super_admin = session.scalar(
            select(UserModel).where(UserModel.role == UserRole.SUPER_ADMIN.value),
        )
        if existing_super_admin is not None:
            print("A super admin already exists. Skipping seed.")
            return

        existing_user = session.scalar(
            select(UserModel).where(UserModel.username == username),
        )
        if existing_user is not None:
            print(f"User '{username}' already exists. Skipping super admin seed.")
            return

        user = UserModel(
            username=username,
            password_hash=PasswordHasher().hash_password(password),
            ldap=False,
            role=UserRole.SUPER_ADMIN.value,
        )
        session.add(user)
        session.commit()

    print(f"Super admin '{username}' created.")


if __name__ == "__main__":
    seed_super_admin()
