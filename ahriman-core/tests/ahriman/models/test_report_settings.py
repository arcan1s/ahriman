from ahriman.models.report_settings import ReportSettings


def test_from_option_invalid() -> None:
    """
    must return disabled on invalid option
    """
    assert ReportSettings.from_option("invalid") == ReportSettings.DISABLED


def test_from_option_valid() -> None:
    """
    must return value from valid options
    """
    assert ReportSettings.from_option("html") == ReportSettings.HTML
    assert ReportSettings.from_option("HTML") == ReportSettings.HTML

    assert ReportSettings.from_option("email") == ReportSettings.EMAIL
    assert ReportSettings.from_option("EmAil") == ReportSettings.EMAIL

    assert ReportSettings.from_option("console") == ReportSettings.CONSOLE
    assert ReportSettings.from_option("conSOle") == ReportSettings.CONSOLE

    assert ReportSettings.from_option("telegram") == ReportSettings.TELEGRAM
    assert ReportSettings.from_option("TElegraM") == ReportSettings.TELEGRAM

    assert ReportSettings.from_option("rss") == ReportSettings.RSS
    assert ReportSettings.from_option("RSS") == ReportSettings.RSS

    assert ReportSettings.from_option("remote-call") == ReportSettings.REMOTE_CALL
    assert ReportSettings.from_option("reMOte-cALL") == ReportSettings.REMOTE_CALL
    assert ReportSettings.from_option("ahriman") == ReportSettings.REMOTE_CALL
    assert ReportSettings.from_option("AhRiMAN") == ReportSettings.REMOTE_CALL
