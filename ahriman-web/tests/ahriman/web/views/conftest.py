import pytest

from aiohttp.web import Application

from ahriman.web.views.base import BaseView


@pytest.fixture
def base(application: Application) -> BaseView:
    """
    base view fixture

    Args:
        application(Application): application fixture

    Returns:
        BaseView: generated base view fixture
    """
    return BaseView(pytest.helpers.request(application, "", ""))
