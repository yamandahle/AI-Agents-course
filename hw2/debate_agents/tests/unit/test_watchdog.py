"""Unit tests for Watchdog — TDD Red phase written before implementation."""

from __future__ import annotations

import threading
from unittest.mock import MagicMock

import pytest

from debate.shared.watchdog import MaxRestartsExceededError, Watchdog

CONFIG = {
    "debate": {
        "watchdog_interval_seconds": 0.001,
        "max_restarts": 2,
    }
}


class FakeProcess:
    """Minimal stand-in for multiprocessing.Process."""

    def __init__(self, alive: bool = True) -> None:
        self._alive = alive
        self.kill_count = 0

    def is_alive(self) -> bool:
        return self._alive

    def kill(self) -> None:
        self.kill_count += 1
        self._alive = False


# ---------------------------------------------------------------------------
# 1. Detects fallen process correctly
# ---------------------------------------------------------------------------
class TestDetection:
    def test_live_process_not_restarted(self) -> None:
        """A live process must not trigger a factory call."""
        wdog = Watchdog(config=CONFIG)
        factory = MagicMock(return_value=FakeProcess(alive=True))
        wdog.register("pro", FakeProcess(alive=True), factory)
        wdog.check_once()
        factory.assert_not_called()

    def test_dead_process_triggers_restart(self) -> None:
        """A dead process must cause the factory to be called exactly once."""
        wdog = Watchdog(config=CONFIG)
        factory = MagicMock(return_value=FakeProcess(alive=True))
        wdog.register("pro", FakeProcess(alive=False), factory)
        wdog.check_once()
        factory.assert_called_once()

    def test_dead_process_is_killed_before_restart(self) -> None:
        """Watchdog must call kill() on the dead process before starting a replacement."""
        wdog = Watchdog(config=CONFIG)
        dead_proc = FakeProcess(alive=False)
        factory = MagicMock(return_value=FakeProcess(alive=True))
        wdog.register("pro", dead_proc, factory)
        wdog.check_once()
        assert dead_proc.kill_count >= 1


# ---------------------------------------------------------------------------
# 2. Restart attempted up to max_restart_attempts from config
# ---------------------------------------------------------------------------
class TestRestartLimit:
    def test_raises_after_max_restarts_exceeded(self) -> None:
        """MaxRestartsExceededError must be raised after max_restarts consecutive failures."""
        wdog = Watchdog(config=CONFIG)
        # Factory always returns a dead process — every restart fails
        factory = MagicMock(return_value=FakeProcess(alive=False))
        wdog.register("pro", FakeProcess(alive=False), factory)

        with pytest.raises(MaxRestartsExceededError):
            for _ in range(CONFIG["debate"]["max_restarts"] + 1):
                wdog.check_once()

    def test_no_error_within_restart_limit(self) -> None:
        """One successful restart must not raise and must call the factory once."""
        wdog = Watchdog(config=CONFIG)
        factory = MagicMock(return_value=FakeProcess(alive=True))
        wdog.register("pro", FakeProcess(alive=False), factory)
        wdog.check_once()  # dead → restart → alive — should not raise
        factory.assert_called_once()

    def test_restart_counter_resets_after_recovery(self) -> None:
        """Restart counter must reset to 0 after a successful restart."""
        wdog = Watchdog(config=CONFIG)
        factory = MagicMock(return_value=FakeProcess(alive=True))
        wdog.register("pro", FakeProcess(alive=False), factory)
        wdog.check_once()
        assert wdog._processes["pro"]["restarts"] == 0  # noqa: SLF001


# ---------------------------------------------------------------------------
# 3. Keep-alive signal works (is_alive=True prevents restart)
# ---------------------------------------------------------------------------
class TestKeepAlive:
    def test_keep_alive_prevents_restart_over_multiple_checks(self) -> None:
        """A healthy process must never trigger a restart regardless of check count."""
        wdog = Watchdog(config=CONFIG)
        factory = MagicMock(return_value=FakeProcess())
        wdog.register("pro", FakeProcess(alive=True), factory)
        for _ in range(5):
            wdog.check_once()
        factory.assert_not_called()

    def test_multiple_processes_checked_independently(self) -> None:
        """Dead process must be restarted while live process is untouched."""
        wdog = Watchdog(config=CONFIG)
        live_factory = MagicMock(return_value=FakeProcess(alive=True))
        dead_factory = MagicMock(return_value=FakeProcess(alive=True))
        wdog.register("pro", FakeProcess(alive=True), live_factory)
        wdog.register("con", FakeProcess(alive=False), dead_factory)
        wdog.check_once()
        live_factory.assert_not_called()
        dead_factory.assert_called_once()


# ---------------------------------------------------------------------------
# 4. Timeout detected (run() exits cleanly; does not hang)
# ---------------------------------------------------------------------------
class TestTimeout:
    def test_stop_halts_run_loop(self) -> None:
        """Calling stop() must cause run() to exit within a reasonable time."""
        wdog = Watchdog(config=CONFIG)

        thread = threading.Thread(target=wdog.run, daemon=True)
        thread.start()
        wdog.stop()
        thread.join(timeout=1.0)

        assert not thread.is_alive(), "run() must exit after stop() is called"

    def test_run_exits_when_max_restarts_exceeded(self) -> None:
        """run() must exit without raising when a process exhausts all restarts."""
        wdog = Watchdog(config=CONFIG)
        factory = MagicMock(return_value=FakeProcess(alive=False))
        wdog.register("pro", FakeProcess(alive=False), factory)

        thread = threading.Thread(target=wdog.run, daemon=True)
        thread.start()
        thread.join(timeout=2.0)

        assert not thread.is_alive(), "run() must self-terminate after MaxRestartsExceededError"
