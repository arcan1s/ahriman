from ahriman.core.auth.auth import Auth
from ahriman.core.auth.mapping_auth import MappingAuth
from ahriman.core.configuration import Configuration
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_load_dummy(configuration: Configuration) -> None:
    """
    must load dummy validator if authorization is not enabled
    """
    configuration.set_option("auth", "target", "disabled")
    auth = Auth.load(configuration)
    assert isinstance(auth, Auth)


def test_load_dummy_empty(configuration: Configuration) -> None:
    """
    must load dummy validator if no option set
    """
    auth = Auth.load(configuration)
    assert isinstance(auth, Auth)


def test_load_mapping(configuration: Configuration) -> None:
    """
    must load mapping validator if option set
    """
    configuration.set_option("auth", "target", "configuration")
    auth = Auth.load(configuration)
    assert isinstance(auth, MappingAuth)


def test_check_credentials(auth: Auth, user: User) -> None:
    """
    must pass any credentials
    """
    assert auth.check_credentials(user.username, user.password)
    assert auth.check_credentials(None, "")
    assert auth.check_credentials("", None)
    assert auth.check_credentials(None, None)


def test_is_safe_request(auth: Auth) -> None:
    """
    must validate safe request
    """
    # login and logout are always safe
    assert auth.is_safe_request("/login", UserAccess.Write)
    assert auth.is_safe_request("/logout", UserAccess.Write)

    auth.allowed_paths.add("/safe")
    auth.allowed_paths_groups.add("/unsafe/safe")

    assert auth.is_safe_request("/safe", UserAccess.Write)
    assert not auth.is_safe_request("/unsafe", UserAccess.Write)
    assert auth.is_safe_request("/unsafe/safe", UserAccess.Write)
    assert auth.is_safe_request("/unsafe/safe/suffix", UserAccess.Write)


def test_is_safe_request_empty(auth: Auth) -> None:
    """
    must not allow requests without path
    """
    assert not auth.is_safe_request(None, UserAccess.Read)
    assert not auth.is_safe_request("", UserAccess.Read)


def test_is_safe_request_read_only(auth: Auth) -> None:
    """
    must allow read-only requests if it is set in settings
    """
    assert auth.is_safe_request("/", UserAccess.Read)
    auth.allow_read_only = True
    assert auth.is_safe_request("/unsafe", UserAccess.Read)


def test_known_username(auth: Auth, user: User) -> None:
    """
    must allow any username
    """
    assert auth.known_username(user.username)


def test_verify_access(auth: Auth, user: User) -> None:
    """
    must allow any access
    """
    assert auth.verify_access(user.username, user.access, None)
    assert auth.verify_access(user.username, UserAccess.Write, None)
