from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.modules.auth.wiring import get_current_user
from app.modules.steam.application.link_steam_account import (
    LinkSteamAccount,
    LinkSteamAccountCommand,
    SteamAccountAlreadyLinkedError,
    SteamProfileLookupError,
    SteamUserNotFoundError,
    UserAlreadyHasSteamAccountError,
)
from app.modules.steam.application.store_steam_game import (
    InvalidSteamGameError,
    StoreSteamGame,
    StoreSteamGameCommand,
)
from app.modules.steam.domain.ports import SteamAccountRepository
from app.modules.steam.entrypoints.schemas import (
    LinkSteamAccountRequest,
    SteamAccountResponse,
    SteamOwnedGamesResponse,
)
from app.modules.steam.wiring import (
    get_link_steam_account,
    get_store_steam_game,
    get_steam_account_repository,
    get_steam_client,
)
from app.modules.users.domain.user import User
from app.shared.infrastructure.providers.steam.steam_client import (
    SteamApiConfigurationError,
    SteamApiError,
    SteamClient,
)


router = APIRouter(prefix="/steam", tags=["steam"])


@router.post("/link", response_model=SteamAccountResponse)
def link_steam_account(
    request: LinkSteamAccountRequest,
    current_user: User = Depends(get_current_user),
    link_steam_account_use_case: LinkSteamAccount = Depends(get_link_steam_account),
) -> SteamAccountResponse:
    try:
        linked_account = link_steam_account_use_case.execute(
            LinkSteamAccountCommand(
                current_user=current_user,
                steam_id_or_vanity=request.steam_id_or_vanity,
            )
        )
    except UserAlreadyHasSteamAccountError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has a linked Steam account",
        )
    except SteamAccountAlreadyLinkedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Steam account is already linked to another user",
        )
    except SteamUserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Steam user not found",
        )
    except SteamProfileLookupError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not validate Steam user",
        )
    except SteamApiConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        )

    return SteamAccountResponse.from_linked(linked_account)


@router.get("/me", response_model=SteamAccountResponse)
def get_my_steam_account(
    current_user: User = Depends(get_current_user),
    steam_account_repository: SteamAccountRepository = Depends(
        get_steam_account_repository
    ),
    steam_client: SteamClient = Depends(get_steam_client),
) -> SteamAccountResponse:
    steam_account = steam_account_repository.get_by_user_id(current_user.id)

    if steam_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Steam account not linked",
        )

    profile = None
    try:
        profile = steam_client.get_player_summary(steam_account.steam_id_64)
    except (SteamApiConfigurationError, SteamApiError):
        profile = None

    return SteamAccountResponse.from_domain(steam_account, profile=profile)


@router.get(
    "/users/{steam_id_or_vanity}/games",
    response_model=SteamOwnedGamesResponse,
)
def get_public_steam_user_games(
    steam_id_or_vanity: str,
    include_played_free_games: bool = Query(default=True),
    language: str = Query(default="english"),
    _current_user: User = Depends(get_current_user),
    steam_client: SteamClient = Depends(get_steam_client),
    store_steam_game: StoreSteamGame = Depends(get_store_steam_game),
) -> SteamOwnedGamesResponse:
    try:
        owned_games = steam_client.get_owned_games(
            steam_id_or_vanity,
            include_played_free_games=include_played_free_games,
            language=language,
        )
    except SteamApiConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        )
    except SteamApiError as error:
        raise HTTPException(
            status_code=error.status_code or status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        )

    for game in owned_games["games"]:
        name = game.get("name")
        appid = game.get("appid")

        if appid is None or name is None:
            continue

        try:
            store_steam_game.execute(StoreSteamGameCommand(appid=appid, name=name))
        except InvalidSteamGameError:
            continue

    return SteamOwnedGamesResponse.model_validate(owned_games)


@router.delete("/link", status_code=status.HTTP_204_NO_CONTENT)
def unlink_steam_account(
    current_user: User = Depends(get_current_user),
    steam_account_repository: SteamAccountRepository = Depends(
        get_steam_account_repository
    ),
) -> Response:
    was_deleted = steam_account_repository.delete_by_user_id(current_user.id)

    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Steam account not linked",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
