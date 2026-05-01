from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.steam.domain.ports import SteamAccountRepository, SteamGameRepository
from app.modules.steam.domain.steam_account import (
    UserSteamAccount,
    UserSteamAccountCreate,
)
from app.modules.steam.domain.steam_game import SteamGame, SteamGameCreate
from app.modules.steam.infrastructure.mappers import (
    steam_game_create_to_model,
    steam_game_model_to_domain,
    steam_account_create_to_model,
    steam_account_model_to_domain,
)
from app.modules.steam.infrastructure.models import SteamGameModel, UserSteamAccountModel


class SqlAlchemySteamAccountRepository(SteamAccountRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_user_id(self, user_id: UUID) -> UserSteamAccount | None:
        statement = select(UserSteamAccountModel).where(
            UserSteamAccountModel.user_id == str(user_id)
        )
        model = self.session.scalar(statement)

        if model is None:
            return None

        return steam_account_model_to_domain(model)

    def get_by_steam_id_64(self, steam_id_64: str) -> UserSteamAccount | None:
        statement = select(UserSteamAccountModel).where(
            UserSteamAccountModel.steam_id_64 == steam_id_64
        )
        model = self.session.scalar(statement)

        if model is None:
            return None

        return steam_account_model_to_domain(model)

    def create(self, steam_account: UserSteamAccountCreate) -> UserSteamAccount:
        model = steam_account_create_to_model(steam_account)

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        return steam_account_model_to_domain(model)

    def delete_by_user_id(self, user_id: UUID) -> bool:
        statement = select(UserSteamAccountModel).where(
            UserSteamAccountModel.user_id == str(user_id)
        )
        model = self.session.scalar(statement)

        if model is None:
            return False

        self.session.delete(model)
        self.session.commit()

        return True


class SqlAlchemySteamGameRepository(SteamGameRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_appid(self, appid: int) -> SteamGame | None:
        statement = select(SteamGameModel).where(SteamGameModel.appid == appid)
        model = self.session.scalar(statement)

        if model is None:
            return None

        return steam_game_model_to_domain(model)

    def create(self, steam_game: SteamGameCreate) -> SteamGame:
        model = steam_game_create_to_model(steam_game)

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        return steam_game_model_to_domain(model)

    def upsert_by_appid(self, appid: int, name: str) -> SteamGame:
        statement = select(SteamGameModel).where(SteamGameModel.appid == appid)
        model = self.session.scalar(statement)

        if model is None:
            return self.create(SteamGameCreate(appid=appid, name=name))

        model.name = name
        self.session.commit()
        self.session.refresh(model)

        return steam_game_model_to_domain(model)
