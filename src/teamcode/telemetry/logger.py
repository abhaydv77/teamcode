from __future__ import annotations

import logging
from typing import Any

from teamcode.telemetry.base import BaseTelemetry

log = logging.getLogger("teamcode.telemetry")


class LoggingTelemetry(BaseTelemetry):
    async def capture(self, event: str, data: dict[str, Any] | None = None) -> None:
        extra = f" {data}" if data else ""
        log.info("[%s]%s", event, extra)
