from ahriman.models.filesystem_package import FilesystemPackage


def test_post_init() -> None:
    """
    must trim versions and descriptions from dependencies list
    """
    assert FilesystemPackage(package_name="p", depends={"a=1"}, opt_depends={"c: a description"}) == \
        FilesystemPackage(package_name="p", depends={"a"}, opt_depends={"c"})


def test_depends_on(filesystem_package: FilesystemPackage) -> None:
    """
    must correctly check package dependencies
    """
    assert filesystem_package.depends_on("dependency", include_optional=False)
    assert not filesystem_package.depends_on("random", include_optional=False)


def test_depends_on_optional(filesystem_package: FilesystemPackage) -> None:
    """
    must correctly check optional dependencies
    """
    assert filesystem_package.depends_on("optional", include_optional=True)
    assert not filesystem_package.depends_on("optional", include_optional=False)
    assert not filesystem_package.depends_on("random", include_optional=True)


def test_is_root_package() -> None:
    """
    must correctly identify root packages
    """
    package = FilesystemPackage(package_name="package", depends={"dependency"}, opt_depends={"optional"})
    dependency = FilesystemPackage(package_name="dependency", depends=set(), opt_depends=set())
    optional = FilesystemPackage(package_name="optional", depends=set(), opt_depends={"package"})
    packages = [package, dependency, optional]

    assert not package.is_root_package(packages, include_optional=True)
    assert not package.is_root_package(packages, include_optional=False)

    assert dependency.is_root_package(packages, include_optional=True)
    assert dependency.is_root_package(packages, include_optional=False)

    assert not optional.is_root_package(packages, include_optional=True)
    assert optional.is_root_package(packages, include_optional=False)


def test_is_root_package_circular() -> None:
    """
    must correctly identify root packages with circular dependencies
    """
    package1 = FilesystemPackage(package_name="package1", depends={"package2"}, opt_depends=set())
    package2 = FilesystemPackage(package_name="package2", depends={"package1"}, opt_depends=set())
    assert package1.is_root_package([package1, package2], include_optional=False)
    assert package2.is_root_package([package1, package2], include_optional=False)

    package1 = FilesystemPackage(package_name="package1", depends=set(), opt_depends={"package2"})
    package2 = FilesystemPackage(package_name="package2", depends=set(), opt_depends={"package1"})
    assert not package1.is_root_package([package1, package2], include_optional=True)
    assert package1.is_root_package([package1, package2], include_optional=False)
