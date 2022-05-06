from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.upload import Rsync


def test_sync(rsync: Rsync, mocker: MockerFixture) -> None:
    """
    must run sync command
    """
    check_output_mock = mocker.patch("ahriman.core.upload.Rsync._check_output")
    rsync.sync(Path("path"), [])
    check_output_mock.assert_called_once_with(*rsync.command, "path", rsync.remote, exception=None, logger=rsync.logger)
