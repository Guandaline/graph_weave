from typing import Dict

from .interfaces import ReadinessCheck


class ReadinessRegistry:
    def __init__(self) -> None:
        self._checks: Dict[str, ReadinessCheck] = {}

    def register(self, check: ReadinessCheck):
        self._checks[check.name] = check

    async def run_all(self) -> Dict[str, str]:
        result = {}
        for name, check in self._checks.items():
            if not check.enabled():
                result[name] = "skipped"
            else:
                try:
                    result[name] = "ok" if await check.check() else "fail"
                except Exception:
                    result[name] = "fail"
        return result


readiness_registry = ReadinessRegistry()
