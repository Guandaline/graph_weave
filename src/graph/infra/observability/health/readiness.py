# graph/fortify/observability/readiness.py

from typing import Awaitable, Callable, Dict

_check_registry: Dict[str, Callable[[], Awaitable[bool]]] = {}


def register_check(name: str):
    def decorator(func: Callable[[], Awaitable[bool]]):
        _check_registry[name] = func
        return func

    return decorator


async def run_readiness_checks() -> Dict[str, str]:
    results = {}
    for name, check_func in _check_registry.items():
        try:
            result = await check_func()
            if result is True:
                results[name] = "ok"
            elif result is False:
                results[name] = "fail"
            else:
                results[name] = "skipped"
        except Exception:
            results[name] = "fail"
    return results
