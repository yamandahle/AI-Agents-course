from __future__ import annotations

from hw4.shared.config import ConfigManager
from hw4.shared.gatekeeper import ApiGatekeeper, RateLimitConfig


class HW4SDK:
    def __init__(self, config_dir: str = "config") -> None:
        self.config = ConfigManager(config_dir)
        self.gatekeeper = self._build_gatekeeper()

    def _build_gatekeeper(self) -> ApiGatekeeper:
        limits = self.config.get_rate_limit("openai")
        return ApiGatekeeper(
            config=RateLimitConfig(
                requests_per_minute=limits["requests_per_minute"],
                requests_per_hour=limits["requests_per_hour"],
                concurrent_max=limits["concurrent_max"],
                retry_after_seconds=limits["retry_after_seconds"],
                max_retries=limits["max_retries"],
            )
        )

    def run_grphify(self) -> None:
        pass

    def run_agents(self) -> None:
        pass

    def detect_bugs(self) -> None:
        pass

    def apply_fix(self) -> None:
        pass

    def verify(self) -> None:
        pass
