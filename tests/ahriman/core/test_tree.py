from ahriman.core.tree import Leaf, Tree
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription


def test_leaf_is_root_empty(leaf_ahriman: Leaf) -> None:
    """
    must be root for empty packages list
    """
    assert leaf_ahriman.is_root([])


def test_leaf_is_root_false(leaf_ahriman: Leaf, leaf_python_schedule: Leaf) -> None:
    """
    must be root for empty dependencies list or if it does not depend on packages
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


def test_tree_resolve(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must resolve denendecnies tree
    """
    tree = Tree.resolve([package_ahriman, package_python_schedule])
    assert len(tree) == 1
    assert len(tree[0]) == 2


def test_tree_levels(leaf_ahriman: Leaf, leaf_python_schedule: Leaf) -> None:
    """
    must generate correct levels in the simples case
    """
    leaf_ahriman.dependencies = set(leaf_python_schedule.package.packages.keys())

    tree = Tree([leaf_ahriman, leaf_python_schedule])
    first, second = tree.levels()
    assert first == [leaf_python_schedule.package]
    assert second == [leaf_ahriman.package]


def test_tree_levels_sorted() -> None:
    """
    must reorder tree, moving packages which are not required for the next level further
    """
    leaf1 = Leaf(
        Package(
            base="package1",
            version="1.0.0",
            remote=None,
            packages={"package1": PackageDescription(depends=[])}
        )
    )
    leaf2 = Leaf(
        Package(
            base="package2",
            version="1.0.0",
            remote=None,
            packages={"package2": PackageDescription(depends=["package1"])}
        )
    )
    leaf3 = Leaf(
        Package(
            base="package3",
            version="1.0.0",
            remote=None,
            packages={"package3": PackageDescription(depends=["package1"])}
        )
    )
    leaf4 = Leaf(
        Package(
            base="package4",
            version="1.0.0",
            remote=None,
            packages={"package4": PackageDescription(depends=["package3"])}
        )
    )

    tree = Tree([leaf1, leaf2, leaf3, leaf4])
    first, second, third = tree.levels()
    assert first == [leaf1.package]
    assert second == [leaf3.package]
    assert third == [leaf2.package, leaf4.package]
