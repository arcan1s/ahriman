from ahriman.models.series_statistics import SeriesStatistics


def test_max() -> None:
    """
    must return maximal value
    """
    assert SeriesStatistics([1, 3, 2]).max == 3


def test_max_empty() -> None:
    """
    must return None as maximal value if series is empty
    """
    assert SeriesStatistics([]).max is None


def test_mean() -> None:
    """
    must return mean value
    """
    assert SeriesStatistics([1, 3, 2]).mean == 2


def test_mean_empty() -> None:
    """
    must return None as mean value if series is empty
    """
    assert SeriesStatistics([]).mean is None


def test_min() -> None:
    """
    must return minimal value
    """
    assert SeriesStatistics([1, 3, 2]).min == 1


def test_min_empty() -> None:
    """
    must return None as minimal value if series is empty
    """
    assert SeriesStatistics([]).min is None


def test_st_dev() -> None:
    """
    must return standard deviation
    """
    assert SeriesStatistics([1, 3, 2]).st_dev == 1


def test_st_dev_empty() -> None:
    """
    must return None as standard deviation if series is empty
    """
    assert SeriesStatistics([]).st_dev is None


def test_st_dev_single() -> None:
    """
    must return 0 as standard deviation if series contains only one element
    """
    assert SeriesStatistics([1]).st_dev == 0


def test_total() -> None:
    """
    must return size of collection
    """
    assert SeriesStatistics([1]).total == 1
    assert SeriesStatistics([]).total == 0


def test_bool() -> None:
    """
    must correctly define empty collection
    """
    assert SeriesStatistics([1])
    assert not SeriesStatistics([])
