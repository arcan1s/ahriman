from ahriman.core.configuration import Configuration
from ahriman.core.report.jinja_template import JinjaTemplate
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_generate(configuration: Configuration, package_ahriman: Package) -> None:
    """
    must generate html report
    """
    path = configuration.getpath("html", "template_path")
    _, repository_id = configuration.check_loaded()
    report = JinjaTemplate(repository_id, configuration, "html")
    assert report.make_html(Result(success=[package_ahriman]), path)
