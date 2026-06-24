"""OllamaServer — optional lifecycle manager for the local Ollama process."""

from __future__ import annotations

import logging
import subprocess
import time
import urllib.request
from urllib.error import URLError

from hw5.shared.config import Config

log = logging.getLogger(__name__)


class OllamaServer:
    """Optionally starts and stops the Ollama server subprocess."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._server_proc: subprocess.Popen[bytes] | None = None

    def ensure_running(self) -> None:
        """Start the server if managed_server=True and it is not yet reachable."""
        if not self._config.get("managed_server", False):
            return
        if self._is_healthy():
            return
        log.info("Starting Ollama server at %s", self._config.ollama_host)
        self._start_server()
        if not self._wait_for_server():
            raise RuntimeError(
                f"Ollama server failed to start within 30 s at {self._config.ollama_host}"
            )

    def stop_server(self) -> None:
        """Terminate the server process if we started it."""
        if self._server_proc is not None:
            self._server_proc.terminate()
            try:
                self._server_proc.wait(timeout=10.0)
            except subprocess.TimeoutExpired:
                self._server_proc.kill()
            self._server_proc = None
            log.info("Ollama server stopped")

    def _start_server(self) -> None:
        self._server_proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _wait_for_server(self, timeout_s: float = 30.0) -> bool:
        """Poll the health endpoint with exponential backoff until ready or timeout."""
        deadline = time.monotonic() + timeout_s
        delay = 0.5
        while time.monotonic() < deadline:
            if self._is_healthy():
                return True
            time.sleep(delay)
            delay = min(delay * 2, 5.0)
        return False

    def _is_healthy(self) -> bool:
        url = f"{self._config.ollama_host}/api/tags"
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except (URLError, OSError):
            return False
