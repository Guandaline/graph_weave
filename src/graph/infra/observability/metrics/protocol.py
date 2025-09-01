from typing import Protocol, runtime_checkable


@runtime_checkable
class MetricProbe(Protocol):
    name: str

    async def update(self) -> None: ...
