import pytest

from pytest_mock import MockerFixture

from ahriman.core.database.sqlite import SQLite
from ahriman.core.tree import Leaf, Tree
from ahriman.models.package import Package


def test_leaf_is_root_empty(leaf_ahriman: Leaf) -> None:
    """
    must be root for empty packages list
    """
    assert leaf_ahriman.is_root([])


def test_leaf_is_root_false(leaf_ahriman: Leaf, leaf_python_schedule: Leaf) -> None:
    """
    must be root for empty dependencies list or if does not depend on packages
    """
    assert leaf_ahriman.is_root([leaf_python_schedule])
    leaf_ahriman.dependencies = {"ahriman-dependency"}
    assert leaf_ahriman.is_root([leaf_python_schedule])


def test_leaf_is_root_true(leaf_ahriman: Leaf, leaf_python_schedule: Leaf) -> None:
    """
    must not be root if depends on packages
    """
    leaf_ahriman.dependencies = {"python-schedule"}
    assert not leaf_ahriman.is_root([leaf_python_schedule])

    leaf_ahriman.dependencies = {"python2-schedule"}
    assert not leaf_ahriman.is_root([leaf_python_schedule])

    leaf_ahriman.dependencies = set(leaf_python_schedule.package.packages.keys())
    assert not leaf_ahriman.is_root([leaf_python_schedule])


def test_leaf_load(package_ahriman: Package, database: SQLite, mocker: MockerFixture) -> None:
    """
    must load with dependencies
    """
    tempdir_mock = mocker.patch("tempfile.mkdtemp")
    load_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.load")
    dependencies_mock = mocker.patch("ahriman.models.package.Package.dependencies", return_value={"ahriman-dependency"})
    rmtree_mock = mocker.patch("shutil.rmtree")

    leaf = Leaf.load(package_ahriman, database)
    assert leaf.package == package_ahriman
    assert leaf.dependencies == {"ahriman-dependency"}
    tempdir_mock.assert_called_once_with()
    load_mock.assert_called_once_with(
        pytest.helpers.anyvar(int), package_ahriman.remote, database.patches_get(package_ahriman.base))
    dependencies_mock.assert_called_once_with(pytest.helpers.anyvar(int))
    rmtree_mock.assert_called_once_with(pytest.helpers.anyvar(int), ignore_errors=True)


def test_tree_levels(leaf_ahriman: Leaf, leaf_python_schedule: Leaf) -> None:
    """
    must generate correct levels in the simples case
    """
    leaf_ahriman.dependencies = set(leaf_python_schedule.package.packages.keys())

    tree = Tree([leaf_ahriman, leaf_python_schedule])
    assert len(tree.levels()) == 2
    first, second = tree.levels()
    assert first == [leaf_python_schedule.package]
    assert second == [leaf_ahriman.package]


def test_tree_load(package_ahriman: Package, package_python_schedule: Package, database: SQLite,
                   mocker: MockerFixture) -> None:
    """
    must package list
    """
    mocker.patch("tempfile.mkdtemp")
    mocker.patch("ahriman.core.build_tools.sources.Sources.load")
    mocker.patch("ahriman.models.package.Package.dependencies")
    mocker.patch("shutil.rmtree")

    tree = Tree.load([package_ahriman, package_python_schedule], database)
    assert len(tree.leaves) == 2
