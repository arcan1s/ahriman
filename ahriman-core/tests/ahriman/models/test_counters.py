from dataclasses import asdict

from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.counters import Counters
from ahriman.models.package import Package


def test_counters_from_json_view(counters: Counters) -> None:
    """
    must construct same object from json
    """
    assert Counters.from_json(asdict(counters)) == counters


def test_counters_from_packages(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must construct object from list of packages with their statuses
    """
    payload = [
        (package_ahriman, BuildStatus(status=BuildStatusEnum.Success)),
        (package_python_schedule, BuildStatus(status=BuildStatusEnum.Failed)),
    ]

    counters = Counters.from_packages(payload)
    assert counters.total == 2
    assert counters.success == 1
    assert counters.failed == 1

    json = asdict(counters)
    total = json.pop("total")
    assert total == sum(i for i in json.values())
