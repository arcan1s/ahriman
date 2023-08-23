from ahriman.models.upload_settings import UploadSettings


def test_from_option_invalid() -> None:
    """
    must return disabled on invalid option
    """
    assert UploadSettings.from_option("invalid") == UploadSettings.Disabled


def test_from_option_valid() -> None:
    """
    must return value from valid options
    """
    assert UploadSettings.from_option("rsync") == UploadSettings.Rsync
    assert UploadSettings.from_option("RSYNC") == UploadSettings.Rsync

    assert UploadSettings.from_option("s3") == UploadSettings.S3
    assert UploadSettings.from_option("S3") == UploadSettings.S3

    assert UploadSettings.from_option("github") == UploadSettings.GitHub
    assert UploadSettings.from_option("GitHub") == UploadSettings.GitHub

    assert UploadSettings.from_option("remote-service") == UploadSettings.RemoteService
    assert UploadSettings.from_option("Remote-Service") == UploadSettings.RemoteService
    assert UploadSettings.from_option("ahriman") == UploadSettings.RemoteService
    assert UploadSettings.from_option("AhRiMAN") == UploadSettings.RemoteService
