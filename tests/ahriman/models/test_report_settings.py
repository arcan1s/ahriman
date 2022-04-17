from ahriman.models.report_settings import ReportSettings


def test_from_option_invalid() -> None:
    """
    must return disabled on invalid option
    """
    assert ReportSettings.from_option("invalid") == ReportSettings.Disabled


def test_from_option_valid() -> None:
    """
    must return value from valid options
    """
    assert ReportSettings.from_option("html") == ReportSettings.HTML
    assert ReportSettings.from_option("HTML") == ReportSettings.HTML

    assert ReportSettings.from_option("email") == ReportSettings.Email
    assert ReportSettings.from_option("EmAil") == ReportSettings.Email

    assert ReportSettings.from_option("console") == ReportSettings.Console
    assert ReportSettings.from_option("conSOle") == ReportSettings.Console

    assert ReportSettings.from_option("telegram") == ReportSettings.Telegram
    assert ReportSettings.from_option("TElegraM") == ReportSettings.Telegram
