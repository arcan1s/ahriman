from ahriman.core.formatters import UpdatePrinter
from ahriman.models.build_plan import BuildPlan, BuildPlanReason
from ahriman.models.package import Package
from ahriman.models.property import Property


def test_properties(update_printer: UpdatePrinter) -> None:
    """
    must return non-empty properties list
    """
    assert update_printer.properties()


def test_properties_na(update_printer: UpdatePrinter) -> None:
    """
    must return N/A if local version is unknown
    """
    package = update_printer.plan.packages[0]
    assert update_printer.properties() == [
        Property(package.base, "", is_required=True),
        Property("N/A", package.version, is_required=True, indent=2, separator=" -> "),
        Property("Reason", BuildPlanReason.RegularUpdate.value, indent=2),
    ]


def test_properties_package_required_by(package_python_schedule: Package) -> None:
    """
    must include requestee package to properties
    """
    plan = BuildPlan()
    plan.add(package_python_schedule, BuildPlanReason.RequiredBy, requester="ahriman")

    properties = list(UpdatePrinter(plan, {}, bump_pkgrel=False).properties_package(package_python_schedule))
    assert properties[-1].value == "required by ahriman"


def test_versions_bump_pkgrel(update_printer: UpdatePrinter) -> None:
    """
    must bump pkgrel if local version is the same
    """
    package = update_printer.plan.packages[0]
    update_printer.local_versions[package.base] = package.version
    assert update_printer.versions(package) == (package.version, "2.6.0-1.1")


def test_versions_keep_pkgrel(update_printer: UpdatePrinter) -> None:
    """
    must keep pkgrel if local version is not the same
    """
    package = update_printer.plan.packages[0]
    update_printer.local_versions[package.base] = "2.5.0-1"
    assert update_printer.versions(package) == ("2.5.0-1", package.version)


def test_versions_no_increment(update_printer: UpdatePrinter) -> None:
    """
    must preserve the package version when release incrementing is disabled
    """
    package = update_printer.plan.packages[0]
    update_printer.local_versions[package.base] = package.version
    update_printer.bump_pkgrel = False

    assert update_printer.versions(package) == (package.version, package.version)


def test_title(update_printer: UpdatePrinter) -> None:
    """
    must return non-empty title
    """
    assert update_printer.title() is not None
