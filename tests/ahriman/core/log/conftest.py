import logging
import pytest

from ahriman.core.log.filtered_access_logger import FilteredAccessLogger


@pytest.fixture
def filtered_access_logger() -> FilteredAccessLogger:
    """
    fixture for custom access logger

    Returns:
        FilteredAccessLogger: custom access logger test instance
    """
    logger = logging.getLogger()
    return FilteredAccessLogger(logger)
