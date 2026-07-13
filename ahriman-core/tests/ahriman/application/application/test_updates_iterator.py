from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.application.updates_iterator import FixedUpdatesIterator, UpdatesIterator
from ahriman.models.package import Package


def test_select_packages(updates_iterator: UpdatesIterator, package_ahriman: Package,
                         package_python_schedule: Package, mocker: MockerFixture) -> None:
    """
    must return next partition
    """
    mocker.patch("ahriman.core.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])

    assert updates_iterator.select_packages() == ([package_python_schedule.base], 2)
    assert updates_iterator.select_packages() == ([package_python_schedule.base], 2)


def test_select_packages_empty(updates_iterator: UpdatesIterator, mocker: MockerFixture) -> None:
    """
    must return None for empty repository
    """
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[])
    assert updates_iterator.select_packages() == (None, 1)


def test_select_packages_cycle(updates_iterator: UpdatesIterator, package_ahriman: Package,
                               package_python_schedule: Package, mocker: MockerFixture) -> None:
    """
    must cycle over partitions
    """
    mocker.patch("ahriman.core.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])

    assert updates_iterator.select_packages() == ([package_python_schedule.base], 2)
    updates_iterator.updated_packages.add(package_python_schedule.base)

    assert updates_iterator.select_packages() == ([package_ahriman.base], 2)
    updates_iterator.updated_packages.add(package_ahriman.base)

    assert updates_iterator.select_packages() == ([package_python_schedule.base], 2)
    assert not updates_iterator.updated_packages


def test_iter(updates_iterator: UpdatesIterator) -> None:
    """
    must return self as iterator
    """
    assert iter(updates_iterator) == updates_iterator


def test_next(updates_iterator: UpdatesIterator, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return next chunk to update
    """
    mocker.patch("ahriman.application.application.updates_iterator.UpdatesIterator.select_packages",
                 side_effect=[([package_ahriman.base], 2), (None, 2), StopIteration])
    sleep_mock = mocker.patch("time.sleep")

    updates = list(updates_iterator)
    assert updates == [[package_ahriman.base], None]
    sleep_mock.assert_has_calls([MockCall(0.5), MockCall(0.5)])


def test_fixed_updates_iterator(fixed_updates_iterator: FixedUpdatesIterator, package_ahriman: Package,
                                mocker: MockerFixture) -> None:
    """
    must always return empty package list
    """
    assert fixed_updates_iterator.select_packages() == ([], 1)

    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[package_ahriman])
    assert fixed_updates_iterator.select_packages() == ([], 1)
