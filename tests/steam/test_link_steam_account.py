import pytest

from app.modules.steam.application.link_steam_account import (
    LinkSteamAccount,
    LinkSteamAccountCommand,
    SteamAccountAlreadyLinkedError,
    SteamProfileLookupError,
    SteamUserNotFoundError,
    UserAlreadyHasSteamAccountError,
)
from app.shared.infrastructure.providers.steam.steam_client import SteamApiError
from tests.fakes import FakeSteamClient


@pytest.mark.unit
def test_link_steam_account_links_profile_found_by_steam_id(
    user_factory,
    steam_account_repository,
) -> None:
    user = user_factory()
    profile = {
        "steamid": "76561198000000000",
        "personaname": "Alice",
    }
    steam_client = FakeSteamClient(profiles={"76561198000000000": profile})
    link_steam_account = LinkSteamAccount(steam_account_repository, steam_client)

    result = link_steam_account.execute(
        LinkSteamAccountCommand(
            current_user=user,
            steam_id_or_vanity="76561198000000000",
        )
    )

    assert result.profile == profile
    assert result.steam_account.user_id == user.id
    assert result.steam_account.steam_id_64 == "76561198000000000"
    assert steam_account_repository.created[0].user_id == user.id
    assert steam_account_repository.created[0].steam_id_64 == "76561198000000000"
    assert steam_client.player_summary_requests == ["76561198000000000"]


@pytest.mark.unit
def test_link_steam_account_stores_steam_id_returned_by_profile(
    user_factory,
    steam_account_repository,
) -> None:
    user = user_factory()
    profile = {
        "steamid": "76561198000000001",
        "personaname": "Vanity Alice",
    }
    steam_client = FakeSteamClient(profiles={"alice-vanity": profile})
    link_steam_account = LinkSteamAccount(steam_account_repository, steam_client)

    result = link_steam_account.execute(
        LinkSteamAccountCommand(
            current_user=user,
            steam_id_or_vanity="alice-vanity",
        )
    )

    assert result.steam_account.steam_id_64 == "76561198000000001"
    assert steam_account_repository.created[0].steam_id_64 == "76561198000000001"
    assert steam_client.player_summary_requests == ["alice-vanity"]


@pytest.mark.unit
def test_link_steam_account_raises_when_user_already_has_link(
    user_factory,
    steam_account_factory,
    steam_account_repository,
) -> None:
    user = user_factory()
    steam_account_repository.add(steam_account_factory(user_id=user.id))
    steam_client = FakeSteamClient(
        profiles={"76561198000000000": {"steamid": "76561198000000000"}}
    )
    link_steam_account = LinkSteamAccount(steam_account_repository, steam_client)

    with pytest.raises(UserAlreadyHasSteamAccountError):
        link_steam_account.execute(
            LinkSteamAccountCommand(
                current_user=user,
                steam_id_or_vanity="76561198000000000",
            )
        )

    assert steam_account_repository.created == []
    assert steam_client.player_summary_requests == []


@pytest.mark.unit
def test_link_steam_account_raises_when_steam_account_is_linked_to_another_user(
    user_factory,
    steam_account_factory,
    steam_account_repository,
) -> None:
    user = user_factory()
    other_user = user_factory(username="other")
    steam_account_repository.add(
        steam_account_factory(
            user_id=other_user.id,
            steam_id_64="76561198000000000",
        )
    )
    steam_client = FakeSteamClient(
        profiles={"alice": {"steamid": "76561198000000000"}}
    )
    link_steam_account = LinkSteamAccount(steam_account_repository, steam_client)

    with pytest.raises(SteamAccountAlreadyLinkedError):
        link_steam_account.execute(
            LinkSteamAccountCommand(current_user=user, steam_id_or_vanity="alice")
        )

    assert steam_account_repository.created == []
    assert steam_client.player_summary_requests == ["alice"]


@pytest.mark.unit
def test_link_steam_account_raises_not_found_when_steam_returns_404(
    user_factory,
    steam_account_repository,
) -> None:
    user = user_factory()
    steam_client = FakeSteamClient(
        errors={"missing": SteamApiError("Steam user not found", status_code=404)}
    )
    link_steam_account = LinkSteamAccount(steam_account_repository, steam_client)

    with pytest.raises(SteamUserNotFoundError):
        link_steam_account.execute(
            LinkSteamAccountCommand(current_user=user, steam_id_or_vanity="missing")
        )

    assert steam_account_repository.created == []


@pytest.mark.unit
def test_link_steam_account_raises_lookup_error_for_other_steam_errors(
    user_factory,
    steam_account_repository,
) -> None:
    user = user_factory()
    steam_client = FakeSteamClient(
        errors={"alice": SteamApiError("Could not reach Steam API")}
    )
    link_steam_account = LinkSteamAccount(steam_account_repository, steam_client)

    with pytest.raises(SteamProfileLookupError):
        link_steam_account.execute(
            LinkSteamAccountCommand(current_user=user, steam_id_or_vanity="alice")
        )

    assert steam_account_repository.created == []
