from pathlib import Path

from ahriman.core.upload.http_upload import HttpUpload


def test_calculate_hash_empty(resource_path_root: Path) -> None:
    """
    must calculate checksum for empty file correctly
    """
    path = resource_path_root / "models" / "empty_file_checksum"
    assert HttpUpload.calculate_hash(path) == "d41d8cd98f00b204e9800998ecf8427e"


def test_calculate_hash_small(resource_path_root: Path) -> None:
    """
    must calculate checksum for path which is single chunk
    """
    path = resource_path_root / "models" / "package_ahriman_pkgbuild"
    assert HttpUpload.calculate_hash(path) == "7136fc388980dc043f9f869d57c5ce0c"


def test_get_body_get_hashes() -> None:
    """
    must generate readable body
    """
    source = {Path("c"): "c_md5", Path("a"): "a_md5", Path("b"): "b_md5"}
    body = HttpUpload.get_body(source)
    parsed = HttpUpload.get_hashes(body)
    assert {fn.name: md5 for fn, md5 in source.items()} == parsed


def test_get_hashes_empty() -> None:
    """
    must read empty body
    """
    assert HttpUpload.get_hashes("") == {}
