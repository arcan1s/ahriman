import aioauth_client
import pytest

from pytest_mock import MockerFixture

from ahriman.core.auth.oauth import OAuth
from ahriman.core.exceptions import OptionError


def test_auth_control(oauth: OAuth) -> None:
    """
    must return a control for authorization
    """
    assert oauth.auth_control
    assert "<a" in oauth.auth_control  # I think it should be a link


def test_get_provider() -> None:
    """
    must return valid provider type
    """
    assert OAuth.get_provider("OAuth2Client") == aioauth_client.OAuth2Client
    assert OAuth.get_provider("GoogleClient") == aioauth_client.GoogleClient
    assert OAuth.get_provider("GithubClient") == aioauth_client.GithubClient


def test_get_provider_not_a_type() -> None:
    """
    must raise an exception if attribute is not a type
    """
    with pytest.raises(OptionError):
        OAuth.get_provider("RANDOM")


def test_get_provider_invalid_type() -> None:
    """
    must raise an exception if attribute is not an OAuth2 client
    """
    with pytest.raises(OptionError):
        OAuth.get_provider("User")
    with pytest.raises(OptionError):
        OAuth.get_provider("OAuth1Client")


def test_get_client(oauth: OAuth) -> None:
    """
    must return valid OAuth2 client
    """
    client = oauth.get_client()
    assert isinstance(client, aioauth_client.GoogleClient)
    assert client.client_id == oauth.client_id
    assert client.client_secret == oauth.client_secret


def test_get_oauth_url(oauth: OAuth, mocker: MockerFixture) -> None:
    """
    must generate valid OAuth authorization URL
    """
    authorize_url_mock = mocker.patch("aioauth_client.GoogleClient.get_authorize_url")
    oauth.get_oauth_url()
    authorize_url_mock.assert_called_once_with(scope=oauth.scopes, redirect_uri=oauth.redirect_uri)


async def test_get_oauth_username(oauth: OAuth, mocker: MockerFixture) -> None:
    """
    must return authorized user ID
    """
    access_token_mock = mocker.patch("aioauth_client.GoogleClient.get_access_token", return_value=("token", ""))
    user_info_mock = mocker.patch("aioauth_client.GoogleClient.user_info",
                                  return_value=(aioauth_client.User(email="email"), ""))

    email = await oauth.get_oauth_username("code")
    access_token_mock.assert_called_once_with("code", redirect_uri=oauth.redirect_uri)
    user_info_mock.assert_called_once_with()
    assert email == "email"


async def test_get_oauth_username_empty_email(oauth: OAuth, mocker: MockerFixture) -> None:
    """
    must read username if email is not available
    """
    mocker.patch("aioauth_client.GoogleClient.get_access_token", return_value=("token", ""))
    mocker.patch("aioauth_client.GoogleClient.user_info", return_value=(aioauth_client.User(username="username"), ""))

    username = await oauth.get_oauth_username("code")
    assert username == "username"


async def test_get_oauth_username_exception_1(oauth: OAuth, mocker: MockerFixture) -> None:
    """
    must return None in case of OAuth request error (get_access_token)
    """
    mocker.patch("aioauth_client.GoogleClient.get_access_token", side_effect=Exception)
    user_info_mock = mocker.patch("aioauth_client.GoogleClient.user_info")

    email = await oauth.get_oauth_username("code")
    assert email is None
    user_info_mock.assert_not_called()


async def test_get_oauth_username_exception_2(oauth: OAuth, mocker: MockerFixture) -> None:
    """
    must return None in case of OAuth request error (user_info)
    """
    mocker.patch("aioauth_client.GoogleClient.get_access_token", return_value=("token", ""))
    mocker.patch("aioauth_client.GoogleClient.user_info", side_effect=Exception)

    email = await oauth.get_oauth_username("code")
    assert email is None
