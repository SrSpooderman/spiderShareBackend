from dataclasses import dataclass

from app.modules.steam.domain.ports import SteamAccountRepository
from app.modules.steam.domain.steam_account import (
    UserSteamAccount,
    UserSteamAccountCreate,
)
from app.modules.users.domain.user import User
from app.shared.infrastructure.providers.steam.steam_client import (
    SteamApiError,
    SteamClient,
)


class SteamAccountAlreadyLinkedError(Exception):
    pass


class UserAlreadyHasSteamAccountError(Exception):
    pass


class SteamUserNotFoundError(Exception):
    pass


class SteamProfileLookupError(Exception):
    pass


@dataclass(frozen=True)
class LinkSteamAccountCommand:
    current_user: User
    steam_id_or_vanity: str


@dataclass(frozen=True)
class LinkedSteamAccount:
    steam_account: UserSteamAccount
    profile: dict


class LinkSteamAccount:
    def __init__(
        self,
        steam_account_repository: SteamAccountRepository,
        steam_client: SteamClient,
    ) -> None:
        self.steam_account_repository = steam_account_repository
        self.steam_client = steam_client

    def execute(self, command: LinkSteamAccountCommand) -> LinkedSteamAccount:
        existing_user_link = self.steam_account_repository.get_by_user_id(
            command.current_user.id
        )
        if existing_user_link is not None:
            raise UserAlreadyHasSteamAccountError

        profile = self._get_public_profile(command.steam_id_or_vanity)
        steam_id_64 = profile["steamid"]

        existing_steam_link = self.steam_account_repository.get_by_steam_id_64(
            steam_id_64
        )
        if existing_steam_link is not None:
            raise SteamAccountAlreadyLinkedError

        steam_account = self.steam_account_repository.create(
            UserSteamAccountCreate(
                user_id=command.current_user.id,
                steam_id_64=steam_id_64,
            )
        )

        return LinkedSteamAccount(steam_account=steam_account, profile=profile)

    def _get_public_profile(self, steam_id_or_vanity: str) -> dict:
        try:
            return self.steam_client.get_player_summary(steam_id_or_vanity)
        except SteamApiError as error:
            if error.status_code == 404:
                raise SteamUserNotFoundError from error

            raise SteamProfileLookupError from error
