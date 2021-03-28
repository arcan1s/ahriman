from ahriman.core.alpm.pacman import Pacman


def test_all_packages(pacman: Pacman) -> None:
    """
    package list must not be empty
    """
    packages = pacman.all_packages()
    assert packages
    assert "pacman" in packages
