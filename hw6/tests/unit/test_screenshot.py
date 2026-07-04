"""Unit tests for ScreenshotCapture -- TDD red phase (Phase 5)."""

from PIL import Image

from cop_thief.gui.screenshot import ScreenshotCapture


def _fake_grab():
    """A real (tiny) image, standing in for a screen grab in tests."""
    return Image.new("RGB", (4, 4))


def test_screenshot_saves_png_to_correct_path(tmp_path):
    capture = ScreenshotCapture(str(tmp_path), "case_a", grab_fn=_fake_grab)
    path = capture.on_subgame_start(1)
    assert path.exists()
    assert path.suffix == ".png"
    assert path.parent == tmp_path / "case_a"


def test_screenshot_filename_includes_case_and_sg_number(tmp_path):
    capture = ScreenshotCapture(str(tmp_path), "case_a", grab_fn=_fake_grab)
    path = capture.on_subgame_start(3)
    assert "case_a" in path.name
    assert "sg3" in path.name


def test_screenshot_dir_created_if_missing(tmp_path):
    target_dir = tmp_path / "does_not_exist_yet"
    capture = ScreenshotCapture(str(target_dir), "case_b", grab_fn=_fake_grab)
    capture.on_game_end()
    assert (target_dir / "case_b").is_dir()


def test_all_5_triggers_produce_files(tmp_path):
    capture = ScreenshotCapture(str(tmp_path), "case_c", grab_fn=_fake_grab)
    paths = [
        capture.on_subgame_start(1),
        capture.on_barrier_placed(1),
        capture.on_cop_wins(1),
        capture.on_thief_wins(2),
        capture.on_game_end(),
    ]
    assert all(p.exists() for p in paths)
    assert len(set(paths)) == 5
