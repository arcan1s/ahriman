from ahriman.core.alpm.pacman import Pacman


def test_all_packages(pacman: Pacman) -> None:
    """
    package list must not be empty
    """
    packages = pacman.all_packages()
    assert packages
    assert "pacman" in packages


def test_all_packages_with_provides(pacman: Pacman) -> None:
    """
    package list must contain provides packages
    """
    assert "sh" in pacman.all_packages()


def test_get(pacman: Pacman) -> None:
    """
    must retrieve package
    """
    assert list(pacman.get("pacman"))


def test_get_empty(pacman: Pacman) -> None:
    """
    must return empty packages list without exception
    """
    assert not list(pacman.get("some-random-name"))
