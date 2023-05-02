from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.support import MirrorlistTrigger


def test_configuration_sections(configuration: Configuration) -> None:
    """
    must correctly parse target list
    """
    configuration.set_option("mirrorlist", "target", "a b c")
    assert MirrorlistTrigger.configuration_sections(configuration) == ["a", "b", "c"]

    configuration.remove_option("mirrorlist", "target")
    assert MirrorlistTrigger.configuration_sections(configuration) == []


def test_on_start(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run report for specified targets
    """
    configuration.set_option("mirrorlist", "target", "mirrorlist")
    run_mock = mocker.patch("ahriman.core.support.package_creator.PackageCreator.run")

    trigger = MirrorlistTrigger("x86_64", configuration)
    trigger.on_start()
    run_mock.assert_called_once_with()
