from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.steam.application.link_steam_account import LinkedSteamAccount
from app.modules.steam.domain.steam_account import UserSteamAccount


class LinkSteamAccountRequest(BaseModel):
    steam_id_or_vanity: str


class SteamPublicProfileResponse(BaseModel):
    steamid: str
    personaname: str | None = None
    profileurl: str | None = None
    avatar: str | None = None
    avatarmedium: str | None = None
    avatarfull: str | None = None


class SteamAccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    steam_id_64: str
    created_at: datetime
    updated_at: datetime
    profile: SteamPublicProfileResponse | None = None

    @classmethod
    def from_domain(
        cls,
        steam_account: UserSteamAccount,
        profile: dict | None = None,
    ) -> "SteamAccountResponse":
        return cls(
            id=steam_account.id,
            user_id=steam_account.user_id,
            steam_id_64=steam_account.steam_id_64,
            created_at=steam_account.created_at,
            updated_at=steam_account.updated_at,
            profile=(
                SteamPublicProfileResponse.model_validate(profile)
                if profile is not None
                else None
            ),
        )

    @classmethod
    def from_linked(
        cls,
        linked_steam_account: LinkedSteamAccount,
    ) -> "SteamAccountResponse":
        return cls.from_domain(
            linked_steam_account.steam_account,
            profile=linked_steam_account.profile,
        )


class SteamOwnedGameResponse(BaseModel):
    appid: int
    name: str | None = None
    playtime_forever: int | None = None
    playtime_2weeks: int | None = None
    img_icon_url: str | None = None
    icon_url: str | None = None
    header_image_url: str | None = None
    capsule_image_url: str | None = None


class SteamOwnedGamesResponse(BaseModel):
    steamid: str
    game_count: int
    games: list[SteamOwnedGameResponse]
