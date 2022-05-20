import pytest

from aiohttp import web

from ahriman.web.views.base import BaseView


@pytest.fixture
def base(application: web.Application) -> BaseView:
    """
    base view fixture

    Args:
        application(web.Application): application fixture

    Returns:
        BaseView: generated base view fixture
    """
    return BaseView(pytest.helpers.request(application, "", ""))
