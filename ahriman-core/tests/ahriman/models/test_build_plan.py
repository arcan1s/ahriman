from dataclasses import replace

from ahriman.models.build_plan import BuildPlan, BuildPlanItem, BuildPlanReason
from ahriman.models.package import Package


def test_add(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must add package into plan
    """
    plan = BuildPlan()

    plan.add(package_ahriman, BuildPlanReason.ManualRequest, requester="later-requester")
    plan.add(package_python_schedule, BuildPlanReason.LocalSourceUpdate)
    assert package_ahriman in plan
    assert package_python_schedule in plan


def test_add_preserves_first_reason(package_ahriman: Package) -> None:
    """
    must update package data while preserving the first reason and requester
    """
    plan = BuildPlan().update([package_ahriman], BuildPlanReason.RegularUpdate, "requester1")
    updated = replace(package_ahriman, version="42")

    plan.add(updated, BuildPlanReason.ManualRequest, "requester2")
    assert plan.item(package_ahriman.base) == BuildPlanItem(updated, BuildPlanReason.RegularUpdate, "requester1")


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

    plan2 = BuildPlan().update([package_ahriman], BuildPlanReason.ManualRequest)
    assert plan1 != plan2


def test_eq_other() -> None:
    """
    must return False in case if object is not an instance of build plan
    """
    assert BuildPlan() != 42
