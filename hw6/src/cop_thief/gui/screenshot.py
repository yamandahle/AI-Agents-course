"""Screenshot capture at the 5 key moments defined in PRD_gui.md section 5."""

from pathlib import Path
from typing import Callable

from PIL import Image, ImageGrab


class ScreenshotCapture:
    """Captures and saves a screenshot for each experiment/game milestone.

    `grab_fn` defaults to `PIL.ImageGrab.grab` but is injectable so tests never
    need a real display -- matches this project's headless-CI test convention.
    """

    def __init__(
        self,
        base_dir: str,
        case_name: str,
        grab_fn: Callable[[], Image.Image] = ImageGrab.grab,
    ) -> None:
        """Store the target directory (per case_name) and the grab function."""
        self.dir = Path(base_dir) / case_name
        self.case_name = case_name
        self._grab = grab_fn

    def on_subgame_start(self, sg_num: int) -> Path:
        """Capture the board at the start of sub-game `sg_num`."""
        return self._save(f"{self.case_name}_sg{sg_num}_start.png")

    def on_barrier_placed(self, sg_num: int) -> Path:
        """Capture the board right after the first barrier of a sub-game."""
        return self._save(f"{self.case_name}_sg{sg_num}_barrier.png")

    def on_cop_wins(self, sg_num: int) -> Path:
        """Capture the board at the moment the Cop captures the Thief."""
        return self._save(f"{self.case_name}_sg{sg_num}_capture.png")

    def on_thief_wins(self, sg_num: int) -> Path:
        """Capture the board when the Thief survives the full sub-game."""
        return self._save(f"{self.case_name}_sg{sg_num}_escape.png")

    def on_game_end(self) -> Path:
        """Capture the final scoreboard after all sub-games complete."""
        return self._save(f"{self.case_name}_final_score.png")

    def _save(self, filename: str) -> Path:
        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.dir / filename
        self._grab().save(path)
        return path
