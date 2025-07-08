import datetime
import json
import pyalpm  # typing: ignore

from dataclasses import asdict, fields, replace
from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any

from ahriman.models.aur_package import AURPackage


def _get_aur_data(resource_path_root: Path) -> dict[str, Any]:
    """
    load package description from resource file

    Args:
        resource_path_root(Path): path to resource root

    Returns:
        dict[str, Any]: json descriptor
    """
    response = (resource_path_root / "models" / "package_ahriman_aur").read_text()
    return json.loads(response)["results"][0]


def _get_official_data(resource_path_root: Path) -> dict[str, Any]:
    """
    load package description from resource file

    Args:
        resource_path_root(Path): path to resource root

    Returns:
        dict[str, Any]: json descriptor
    """
    response = (resource_path_root / "models" / "package_akonadi_aur").read_text()
    return json.loads(response)["results"][0]


def test_post_init(aur_package_ahriman: AURPackage) -> None:
    """
    must trim versions and descriptions from packages list
    """
    package = replace(
        aur_package_ahriman,
        depends=["a=1"],
        make_depends=["b>=3"],
        opt_depends=["c: a description"],
        check_depends=["d=4"],
        provides=["e=5"],
    )
    assert package.depends == ["a"]
    assert package.make_depends == ["b"]
    assert package.opt_depends == ["c"]
    assert package.check_depends == ["d"]
    assert package.provides == ["e"]


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


def test_from_pacman(pyalpm_package_ahriman: pyalpm.Package, aur_package_ahriman: AURPackage) -> None:
    """
    must load package from repository database
    """
    model = AURPackage.from_pacman(pyalpm_package_ahriman)
    # some fields are missing so we are changing them
    object.__setattr__(model, "id", aur_package_ahriman.id)
    object.__setattr__(model, "package_base_id", aur_package_ahriman.package_base_id)
    object.__setattr__(model, "first_submitted", aur_package_ahriman.first_submitted)
    object.__setattr__(model, "url_path", aur_package_ahriman.url_path)
    object.__setattr__(model, "maintainer", aur_package_ahriman.maintainer)
    object.__setattr__(model, "submitter", aur_package_ahriman.submitter)

    assert model == aur_package_ahriman


def test_from_repo(aur_package_akonadi: AURPackage, resource_path_root: Path) -> None:
    """
    must load package from repository api json
    """
    model = _get_official_data(resource_path_root)
    assert AURPackage.from_repo(model) == aur_package_akonadi


def test_convert(resource_path_root: Path) -> None:
    """
    must convert fields to snakecase and also apply converters
    """
    model = _get_aur_data(resource_path_root)
    converted = AURPackage.convert(model)
    known_fields = [pair.name for pair in fields(AURPackage)]
    assert all(field in known_fields for field in converted)
    assert isinstance(converted.get("first_submitted"), datetime.datetime)
    assert isinstance(converted.get("last_modified"), datetime.datetime)
