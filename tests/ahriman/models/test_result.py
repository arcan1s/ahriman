import pytest

from ahriman.core.exceptions import SuccessFailed
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_is_empty() -> None:
    """
    must return is empty for empty builds
    """
    result = Result()
    assert result.is_empty


def test_non_empty_success(package_ahriman: Package) -> None:
    """
    must be non-empty if there is success build
    """
    result = Result()
    result.add_success(package_ahriman)
    assert not result.is_empty


def test_is_empty_failed(package_ahriman: Package) -> None:
    """
    must be empty if there is only failed build
    """
    result = Result()
    result.add_failed(package_ahriman)
    assert result.is_empty


def test_non_empty_full(package_ahriman: Package) -> None:
    """
    must be non-empty if there are both failed and success builds
    """
    result = Result()
    result.add_failed(package_ahriman)
    result.add_success(package_ahriman)

    assert not result.is_empty


def test_add_failed(package_ahriman: Package) -> None:
    """
    must add package to failed list
    """
    result = Result()
    result.add_failed(package_ahriman)
    assert result.failed == [package_ahriman]
    assert not result.success


def test_add_success(package_ahriman: Package) -> None:
    """
    must add package to success list
    """
    result = Result()
    result.add_success(package_ahriman)
    assert result.success == [package_ahriman]
    assert not result.failed


def test_merge(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must merge success packages
    """
    left = Result()
    left.add_success(package_ahriman)
    right = Result()
    right.add_success(package_python_schedule)

    result = left.merge(right)
    assert result.success == [package_ahriman, package_python_schedule]
    assert not left.failed


def test_merge_failed(package_ahriman: Package) -> None:
    """
    must merge and remove failed packages from success list
    """
    left = Result()
    left.add_success(package_ahriman)
    right = Result()
    right.add_failed(package_ahriman)

    result = left.merge(right)
    assert result.failed == [package_ahriman]
    assert not left.success


def test_merge_exception(package_ahriman: Package) -> None:
    """
    must raise exception in case if package was failed
    """
    left = Result()
    left.add_failed(package_ahriman)
    right = Result()
    right.add_success(package_ahriman)

    with pytest.raises(SuccessFailed):
        left.merge(right)


def test_eq(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must return True for same objects
    """
    left = Result()
    left.add_success(package_ahriman)
    left.add_failed(package_python_schedule)
    right = Result()
    right.add_success(package_ahriman)
    right.add_failed(package_python_schedule)

    assert left == right


def test_eq_false(package_ahriman: Package) -> None:
    """
    must return False in case if lists do not match
    """
    left = Result()
    left.add_success(package_ahriman)
    right = Result()
    right.add_failed(package_ahriman)

    assert left != right


def test_eq_false_failed(package_ahriman: Package) -> None:
    """
    must return False in case if failed does not match
    """
    left = Result()
    left.add_failed(package_ahriman)

    assert left != Result()


def test_eq_false_success(package_ahriman: Package) -> None:
    """
    must return False in case if success does not match
    """
    left = Result()
    left.add_success(package_ahriman)

    assert left != Result()


def test_eq_other() -> None:
    """
    must return False in case if object is not an instance of result
    """
    assert Result() != 42
