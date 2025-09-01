from typing import Protocol, runtime_checkable


@runtime_checkable
class ReadinessCheck(Protocol):
    name: str

    def enabled(self) -> bool: ...

    async def check(self) -> bool: ...
