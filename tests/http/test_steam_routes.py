from dataclasses import dataclass

import pytest

from app.modules.auth.wiring import get_current_user
from app.modules.steam.application.link_steam_account import (
    LinkedSteamAccount,
    SteamAccountAlreadyLinkedError,
    SteamProfileLookupError,
    SteamUserNotFoundError,
    UserAlreadyHasSteamAccountError,
)
from app.modules.steam.application.store_steam_game import StoreSteamGame
from app.modules.steam.wiring import (
    get_link_steam_account,
    get_steam_account_repository,
    get_steam_client,
    get_store_steam_game,
)
from app.shared.infrastructure.providers.steam.steam_client import SteamApiError
from tests.fakes import FakeSteamClient


@dataclass
class StubLinkSteamAccount:
    result: LinkedSteamAccount | None = None
    error: Exception | None = None

    def execute(self, command):
        self.command = command
        if self.error is not None:
            raise self.error

        return self.result


@pytest.mark.http
def test_link_steam_account_returns_linked_account(
    app,
    client,
    user_factory,
    steam_account_factory,
) -> None:
    current_user = user_factory(username="alice")
    steam_account = steam_account_factory(user_id=current_user.id)
    profile = {
        "steamid": steam_account.steam_id_64,
        "personaname": "Alice",
        "profileurl": "https://steamcommunity.com/id/alice/",
    }
    use_case = StubLinkSteamAccount(
        result=LinkedSteamAccount(steam_account=steam_account, profile=profile)
    )
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_link_steam_account] = lambda: use_case

    response = client.post(
        "/steam/link",
        json={"steam_id_or_vanity": "alice"},
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == str(current_user.id)
    assert response.json()["steam_id_64"] == steam_account.steam_id_64
    assert response.json()["profile"]["personaname"] == "Alice"
    assert use_case.command.current_user == current_user
    assert use_case.command.steam_id_or_vanity == "alice"


@pytest.mark.http
@pytest.mark.parametrize(
    ("error", "expected_status", "expected_detail"),
    [
        (
            UserAlreadyHasSteamAccountError(),
            409,
            "User already has a linked Steam account",
        ),
        (
            SteamAccountAlreadyLinkedError(),
            409,
            "Steam account is already linked to another user",
        ),
        (SteamUserNotFoundError(), 404, "Steam user not found"),
        (SteamProfileLookupError(), 502, "Could not validate Steam user"),
    ],
)
def test_link_steam_account_maps_use_case_errors_to_http(
    app,
    client,
    user_factory,
    error: Exception,
    expected_status: int,
    expected_detail: str,
) -> None:
    current_user = user_factory(username="alice")
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_link_steam_account] = lambda: StubLinkSteamAccount(
        error=error
    )

    response = client.post(
        "/steam/link",
        json={"steam_id_or_vanity": "alice"},
    )

    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail


@pytest.mark.http
def test_get_my_steam_account_returns_account_and_profile(
    app,
    client,
    user_factory,
    steam_account_factory,
    steam_account_repository,
) -> None:
    current_user = user_factory(username="alice")
    steam_account = steam_account_factory(user_id=current_user.id)
    steam_account_repository.add(steam_account)
    steam_client = FakeSteamClient(
        profiles={
            steam_account.steam_id_64: {
                "steamid": steam_account.steam_id_64,
                "personaname": "Alice",
            }
        }
    )
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_steam_account_repository] = (
        lambda: steam_account_repository
    )
    app.dependency_overrides[get_steam_client] = lambda: steam_client

    response = client.get("/steam/me")

    assert response.status_code == 200
    assert response.json()["steam_id_64"] == steam_account.steam_id_64
    assert response.json()["profile"]["personaname"] == "Alice"


@pytest.mark.http
def test_get_my_steam_account_returns_profile_null_when_steam_refresh_fails(
    app,
    client,
    user_factory,
    steam_account_factory,
    steam_account_repository,
) -> None:
    current_user = user_factory(username="alice")
    steam_account = steam_account_factory(user_id=current_user.id)
    steam_account_repository.add(steam_account)
    steam_client = FakeSteamClient(
        errors={steam_account.steam_id_64: SteamApiError("Steam unavailable")}
    )
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_steam_account_repository] = (
        lambda: steam_account_repository
    )
    app.dependency_overrides[get_steam_client] = lambda: steam_client

    response = client.get("/steam/me")

    assert response.status_code == 200
    assert response.json()["steam_id_64"] == steam_account.steam_id_64
    assert response.json()["profile"] is None


@pytest.mark.http
def test_get_my_steam_account_returns_404_without_link(
    app,
    client,
    user_factory,
    steam_account_repository,
) -> None:
    current_user = user_factory(username="alice")
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_steam_account_repository] = (
        lambda: steam_account_repository
    )
    app.dependency_overrides[get_steam_client] = lambda: FakeSteamClient()

    response = client.get("/steam/me")

    assert response.status_code == 404
    assert response.json()["detail"] == "Steam account not linked"


@pytest.mark.http
def test_get_public_steam_user_games_returns_games_and_stores_valid_ones(
    app,
    client,
    user_factory,
    steam_game_repository,
) -> None:
    current_user = user_factory(username="alice")
    steam_client = FakeSteamClient(
        owned_games={
            "alice": {
                "steamid": "76561198000000000",
                "game_count": 3,
                "games": [
                    {"appid": 10, "name": "Counter-Strike"},
                    {"appid": 20},
                    {"name": "Missing appid"},
                ],
            }
        }
    )
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_steam_client] = lambda: steam_client
    app.dependency_overrides[get_store_steam_game] = lambda: StoreSteamGame(
        steam_game_repository
    )

    response = client.get("/steam/users/alice/games?language=spanish")

    assert response.status_code == 200
    assert response.json()["steamid"] == "76561198000000000"
    assert response.json()["game_count"] == 3
    assert steam_client.owned_games_requests == [("alice", True, "spanish")]
    assert steam_game_repository.upserted == [(10, "Counter-Strike")]


@pytest.mark.http
def test_get_public_steam_user_games_maps_steam_api_error_status(
    app,
    client,
    user_factory,
) -> None:
    current_user = user_factory(username="alice")
    steam_client = FakeSteamClient(
        errors={"alice": SteamApiError("Private profile", status_code=403)}
    )
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_steam_client] = lambda: steam_client
    app.dependency_overrides[get_store_steam_game] = lambda: StoreSteamGame(
        steam_game_repository=None
    )

    response = client.get("/steam/users/alice/games")

    assert response.status_code == 403
    assert response.json()["detail"] == "Private profile"


@pytest.mark.http
def test_unlink_steam_account_returns_204_when_link_exists(
    app,
    client,
    user_factory,
    steam_account_factory,
    steam_account_repository,
) -> None:
    current_user = user_factory(username="alice")
    steam_account_repository.add(steam_account_factory(user_id=current_user.id))
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_steam_account_repository] = (
        lambda: steam_account_repository
    )

    response = client.delete("/steam/link")

    assert response.status_code == 204
    assert steam_account_repository.get_by_user_id(current_user.id) is None


@pytest.mark.http
def test_unlink_steam_account_returns_404_when_link_is_missing(
    app,
    client,
    user_factory,
    steam_account_repository,
) -> None:
    current_user = user_factory(username="alice")
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_steam_account_repository] = (
        lambda: steam_account_repository
    )

    response = client.delete("/steam/link")

    assert response.status_code == 404
    assert response.json()["detail"] == "Steam account not linked"
