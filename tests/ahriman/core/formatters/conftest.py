import pytest

from pathlib import Path

from ahriman.core.formatters import \
    AurPrinter, \
    ChangesPrinter, \
    ConfigurationPathsPrinter, \
    ConfigurationPrinter, \
    EventStatsPrinter, \
    PackagePrinter, \
    PackageStatsPrinter, \
    PatchPrinter, \
    RepositoryPrinter, \
    RepositoryStatsPrinter, \
    StatusPrinter, \
    StringPrinter, \
    TreePrinter, \
    UpdatePrinter, \
    UserPrinter, \
    ValidationPrinter, \
    VersionPrinter
from ahriman.models.aur_package import AURPackage
from ahriman.models.build_status import BuildStatus
from ahriman.models.changes import Changes
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_stats import RepositoryStats
from ahriman.models.user import User


@pytest.fixture
def aur_package_ahriman_printer(aur_package_ahriman: AURPackage) -> AurPrinter:
    """
    fixture for AUR package printer

    Args:
        aur_package_ahriman(AURPackage): AUR package fixture

    Returns:
        AurPrinter: AUR package printer test instance
    """
    return AurPrinter(aur_package_ahriman)


@pytest.fixture
def changes_printer() -> ChangesPrinter:
    """
    fixture for changes printer

    Returns:
        ChangesPrinter: changes printer test instance
    """
    return ChangesPrinter(Changes("sha", "changes"))


@pytest.fixture
def configuration_paths_printer() -> ConfigurationPathsPrinter:
    """
    fixture for configuration paths printer

    Returns:
        ConfigurationPathsPrinter: configuration paths printer test instance
    """
    return ConfigurationPathsPrinter(Path("root"), [Path("include1"), Path("include2")])


@pytest.fixture
def configuration_printer() -> ConfigurationPrinter:
    """
    fixture for configuration printer

    Returns:
        ConfigurationPrinter: configuration printer test instance
    """
    return ConfigurationPrinter("section", {"key_one": "value_one", "key_two": "value_two"})


@pytest.fixture
def event_stats_printer() -> EventStatsPrinter:
    """
    fixture for event stats printer

    Returns:
        EventStatsPrinter: event stats printer test instance
    """
    return EventStatsPrinter("event", [5, 2, 7, 9, 8, 0, 4, 1, 6, 3])


@pytest.fixture
def package_ahriman_printer(package_ahriman: Package) -> PackagePrinter:
    """
    fixture for package printer

    Args:
        package_ahriman(Package): package fixture

    Returns:
        PackagePrinter: package printer test instance
    """
    return PackagePrinter(package_ahriman, BuildStatus())


@pytest.fixture
def package_stats_printer(package_ahriman: Package, package_python_schedule: Package) -> PackageStatsPrinter:
    """
    fixture for package stats printer

    Args:
        package_ahriman(Package): package fixture
        package_python_schedule(Package): schedule package fixture

    Returns:
        PackageStatsPrinter: package stats printer test instance
    """
    return PackageStatsPrinter({package_ahriman.base: 4, package_python_schedule.base: 5})


@pytest.fixture
def patch_printer(package_ahriman: Package) -> PatchPrinter:
    """
    fixture for patch printer

    Args:
        package_ahriman(Package): package fixture

    Returns:
        PatchPrinter: patch printer test instance
    """
    return PatchPrinter(package_ahriman.base, [PkgbuildPatch("key", "value")])


@pytest.fixture
def repository_printer(repository_id: RepositoryId) -> RepositoryPrinter:
    """
    fixture for repository printer

    Args:
        repository_id(RepositoryId): repository identifier fixture

    Returns:
        RepositoryPrinter: repository printer test instance
    """
    return RepositoryPrinter(repository_id)


@pytest.fixture
def repository_stats_printer(repository_id: RepositoryId) -> RepositoryStatsPrinter:
    """
    fixture for repository stats printer

    Args:
        repository_id(RepositoryId): repository identifier fixture

    Returns:
        RepositoryStatsPrinter: repository stats printer test instance
    """
    return RepositoryStatsPrinter(repository_id, RepositoryStats(bases=1, packages=2, archive_size=3, installed_size=4))


@pytest.fixture
def status_printer() -> StatusPrinter:
    """
    fixture for build status printer

    Returns:
        StatusPrinter: build status printer test instance
    """
    return StatusPrinter(BuildStatus())


@pytest.fixture
def string_printer() -> StringPrinter:
    """
    fixture for any string printer

    Returns:
        StringPrinter: any string printer test instance
    """
    return StringPrinter("hello, world")


@pytest.fixture
def tree_printer(package_ahriman: Package) -> TreePrinter:
    """
    fixture for tree printer

    Args:
        package_ahriman(Package): package fixture

    Returns:
        TreePrinter: tree printer test instance
    """
    return TreePrinter(0, [package_ahriman])


@pytest.fixture
def update_printer(package_ahriman: Package) -> UpdatePrinter:
    """
    fixture for update printer

    Args:
        package_ahriman(Package): package fixture

    Returns:
        UpdatePrinter: update printer test instance
    """
    return UpdatePrinter(package_ahriman, None)


@pytest.fixture
def user_printer(user: User) -> UserPrinter:
    """
    fixture for user printer

    Args:
        user(User): user fixture

    Returns:
        UserPrinter: user printer test instance
    """
    return UserPrinter(user)


@pytest.fixture
def validation_printer() -> ValidationPrinter:
    """
    fixture for validation printer

    Returns:
        ValidationPrinter: validation printer test instance
    """
    return ValidationPrinter("root", [
        "root error",
        {
            "child": [
                "child error",
                {
                    "grandchild": [
                        "grandchild error",
                    ],
                },
            ],
        },
    ])


@pytest.fixture
def version_printer(package_ahriman: Package) -> VersionPrinter:
    """
    fixture for version printer

    Args:
        package_ahriman(Package): package fixture

    Returns:
        VersionPrinter: version printer test instance
    """
    return VersionPrinter("package", {package_ahriman.base: package_ahriman.version})
