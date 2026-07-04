import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sorter import category_for, plan_moves  # noqa: E402


def test_category_for_images():
    assert category_for(Path("photo.JPG")) == "images"
    assert category_for(Path("scan.pdf")) == "documents"
    assert category_for(Path("archive.tar.gz")) == "archives"
    assert category_for(Path("unknown.xyz")) == "other"


def test_plan_moves_by_type(tmp_path):
    (tmp_path / "a.png").write_text("x")
    (tmp_path / "b.pdf").write_text("x")
    (tmp_path / ".hidden").write_text("x")

    moves = plan_moves(tmp_path, mode="type")
    names = {src.name: dst.parent.name for src, dst in moves}

    assert names == {"a.png": "images", "b.pdf": "documents"}


def test_plan_moves_avoids_name_collision(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "a.png").write_text("existing")
    (tmp_path / "a.png").write_text("new")

    moves = plan_moves(tmp_path, mode="type")
    _, destination = moves[0]

    assert destination.name == "a_1.png"


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
