from ahriman.core.configuration import Configuration
from ahriman.core.report.jinja_template import JinjaTemplate
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_generate(configuration: Configuration, package_ahriman: Package) -> None:
    """
    must generate html report
    """
    name = configuration.getpath("html", "template")
    _, repository_id = configuration.check_loaded()
    report = JinjaTemplate(repository_id, configuration, "html")
    assert report.make_html(Result(updated=[package_ahriman]), name)


def test_generate_from_path(configuration: Configuration, package_ahriman: Package) -> None:
    """
    must generate html report from path
    """
    path = configuration.getpath("html", "templates") / configuration.get("html", "template")
    _, repository_id = configuration.check_loaded()
    report = JinjaTemplate(repository_id, configuration, "html")
    assert report.make_html(Result(updated=[package_ahriman]), path)
