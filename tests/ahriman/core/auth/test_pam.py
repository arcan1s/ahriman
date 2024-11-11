from pytest_mock import MockerFixture

from ahriman.core.auth.pam import PAM
from ahriman.core.exceptions import CalledProcessError
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_group_members() -> None:
    """
    must return current group members
    """
    assert "root" in PAM.group_members("root")


def test_group_members_unknown() -> None:
    """
    must return empty list for unknown group
    """
    assert not PAM.group_members("somerandomgroupname")


async def test_check_credentials(pam: PAM, user: User, mocker: MockerFixture) -> None:
    """
    must correctly check user credentials via PAM
    """
    authenticate_mock = mocker.patch("ahriman.core.auth.pam.check_output")
    mapping_mock = mocker.patch("ahriman.core.auth.mapping.Mapping.check_credentials")

    assert await pam.check_credentials(user.username, user.password)
    authenticate_mock.assert_called_once_with("su", "--command", "true", "-", user.username,
                                              input_data=user.password)
    mapping_mock.assert_not_called()


async def test_check_credentials_empty(pam: PAM) -> None:
    """
    must reject on empty credentials
    """
    assert not await pam.check_credentials("", None)


async def test_check_credentials_root(pam: PAM, user: User, mocker: MockerFixture) -> None:
    """
    must reject on root logon attempt
    """
    mocker.patch("ahriman.core.auth.pam.check_output")
    assert not await pam.check_credentials("root", user.password)

    pam.permit_root_login = True
    assert await pam.check_credentials("root", user.password)


async def test_check_credentials_mapping(pam: PAM, user: User, mocker: MockerFixture) -> None:
    """
    must correctly check user credentials via database if PAM rejected
    """
    mocker.patch("ahriman.core.auth.pam.check_output",
                 side_effect=CalledProcessError(1, ["command"], "error"))
    mapping_mock = mocker.patch("ahriman.core.auth.mapping.Mapping.check_credentials")

    await pam.check_credentials(user.username, user.password)
    mapping_mock.assert_called_once_with(pam, user.username, user.password)


async def test_known_username(pam: PAM, user: User, mocker: MockerFixture) -> None:
    """
    must check if user exists in system
    """
    getpwnam_mock = mocker.patch("ahriman.core.auth.pam.getpwnam")
    mapping_mock = mocker.patch("ahriman.core.auth.mapping.Mapping.known_username")

    assert await pam.known_username(user.username)
    getpwnam_mock.assert_called_once_with(user.username)
    mapping_mock.assert_not_called()


async def test_known_username_mapping(pam: PAM, user: User, mocker: MockerFixture) -> None:
    """
    must fall back to username checking to database if no user found in system
    """
    mocker.patch("ahriman.core.auth.pam.getpwnam", side_effect=KeyError)
    mapping_mock = mocker.patch("ahriman.core.auth.mapping.Mapping.known_username")

    await pam.known_username(user.username)
    mapping_mock.assert_called_once_with(pam, user.username)


async def test_verify_access(pam: PAM, user: User, mocker: MockerFixture) -> None:
    """
    must verify user access via PAM groups
    """
    mocker.patch("ahriman.core.auth.pam.PAM.get_user", return_value=None)
    mocker.patch("ahriman.core.auth.pam.PAM.group_members", return_value=[user.username])
    assert await pam.verify_access(user.username, UserAccess.Full, None)


async def test_verify_access_readonly(pam: PAM, user: User, mocker: MockerFixture) -> None:
    """
    must set user access to read only if it doesn't belong to the admin group
    """
    mocker.patch("ahriman.core.auth.pam.PAM.get_user", return_value=None)
    mocker.patch("ahriman.core.auth.pam.PAM.group_members", return_value=[])

    assert not await pam.verify_access(user.username, UserAccess.Full, None)
    assert not await pam.verify_access(user.username, UserAccess.Reporter, None)
    assert await pam.verify_access(user.username, UserAccess.Read, None)


async def test_verify_access_override(pam: PAM, user: User, mocker: MockerFixture) -> None:
    """
    must verify user access via database if there is override
    """
    mocker.patch("ahriman.core.auth.pam.PAM.get_user", return_value=user)
    group_mock = mocker.patch("ahriman.core.auth.pam.PAM.group_members")

    assert await pam.verify_access(user.username, user.access, None)
    group_mock.assert_not_called()
