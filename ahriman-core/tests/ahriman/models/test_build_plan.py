from ahriman.models.build_plan import BuildPlan, BuildPlanReason
from ahriman.models.package import Package


def test_add(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must replace the package and reason for the same base
    """
    plan = BuildPlan().update([package_ahriman], BuildPlanReason.RegularUpdate)
    plan.add(package_ahriman, BuildPlanReason.QueuedRequest)
    plan.add(package_python_schedule, BuildPlanReason.LocalSourceUpdate)

    assert package_ahriman in plan
    assert package_python_schedule in plan
    assert plan.item(package_ahriman.base).reason == BuildPlanReason.QueuedRequest


def test_add_with_requester(package_python_schedule: Package) -> None:
    """
    must keep the last requester for a dependency
    """
    plan = BuildPlan()
    plan.add(package_python_schedule, BuildPlanReason.RequiredBy, requester="ahriman")
    plan.add(package_python_schedule, BuildPlanReason.RequiredBy, requester="python-ahriman")

    assert plan.item(package_python_schedule.base).requester == "python-ahriman"


def test_update(package_ahriman: Package) -> None:
    """
    must update instance with new packages
    """
    plan = BuildPlan().update([package_ahriman], BuildPlanReason.RegularUpdate)
    assert package_ahriman in plan


def test_eq(package_ahriman: Package) -> None:
    """
    must compare two plans
    """
    plan1 = BuildPlan().update([package_ahriman], BuildPlanReason.RegularUpdate)
    assert plan1 == plan1

    plan2 = BuildPlan().update([package_ahriman], BuildPlanReason.QueuedRequest)
    assert plan1 != plan2


def test_eq_other() -> None:
    """
    must return False in case if object is not an instance of build plan
    """
    assert BuildPlan() != 42
