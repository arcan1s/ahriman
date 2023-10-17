import pytest

from pytest_mock import MockerFixture

from ahriman.core.exceptions import MigrationError
from ahriman.models.migration_result import MigrationResult


def test_is_outdated() -> None:
    """
    must return False for outdated schema
    """
    assert MigrationResult(old_version=0, new_version=1).is_outdated
    assert not MigrationResult(old_version=1, new_version=1).is_outdated


def test_is_outdated_validation(mocker: MockerFixture) -> None:
    """
    must call validation before version check
    """
    validate_mock = mocker.patch("ahriman.models.migration_result.MigrationResult.validate")
    assert MigrationResult(old_version=0, new_version=1).is_outdated
    validate_mock.assert_called_once_with()


def test_validate() -> None:
    """
    must raise exception on invalid migration versions
    """
    with pytest.raises(MigrationError):
        MigrationResult(old_version=-1, new_version=0).validate()

    with pytest.raises(MigrationError):
        MigrationResult(old_version=1, new_version=0).validate()
