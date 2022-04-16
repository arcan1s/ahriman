import datetime
import json

from dataclasses import asdict, fields
from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any, Dict

from ahriman.models.aur_package import AURPackage


def _get_aur_data(resource_path_root: Path) -> Dict[str, Any]:
    """
    load package description from resource file

    Args:
      resource_path_root(Path): path to resource root

    Returns:
      Dict[str, Any]: json descriptor
    """
    response = (resource_path_root / "models" / "package_ahriman_aur").read_text()
    return json.loads(response)["results"][0]


def _get_official_data(resource_path_root: Path) -> Dict[str, Any]:
    """
    load package description from resource file

    Args:
      resource_path_root(Path): path to resource root

    Returns:
      Dict[str, Any]: json descriptor
    """
    response = (resource_path_root / "models" / "package_akonadi_aur").read_text()
    return json.loads(response)["results"][0]


def test_from_json(aur_package_ahriman: AURPackage, resource_path_root: Path) -> None:
    """
    must load package from json
    """
    model = _get_aur_data(resource_path_root)
    assert AURPackage.from_json(model) == aur_package_ahriman


def test_from_json_2(aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must load the same package from json
    """
    mocker.patch("ahriman.models.aur_package.AURPackage.convert", side_effect=lambda v: v)
    assert AURPackage.from_json(asdict(aur_package_ahriman)) == aur_package_ahriman


def test_from_repo(aur_package_akonadi: AURPackage, resource_path_root: Path) -> None:
    """
    must load package from repository api json
    """
    model = _get_official_data(resource_path_root)
    assert AURPackage.from_repo(model) == aur_package_akonadi


def test_convert(aur_package_ahriman: AURPackage, resource_path_root: Path) -> None:
    """
    must convert fields to snakecase and also apply converters
    """
    model = _get_aur_data(resource_path_root)
    converted = AURPackage.convert(model)
    known_fields = [pair.name for pair in fields(AURPackage)]
    assert all(field in known_fields for field in converted)
    assert isinstance(converted.get("first_submitted"), datetime.datetime)
    assert isinstance(converted.get("last_modified"), datetime.datetime)
