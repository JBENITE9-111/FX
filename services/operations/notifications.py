from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from services.operations.store import due_deliveries, queue_delivery, update_delivery


def channel_health() -> dict:
    return {
        "app": {"status": "CONNECTED", "detail": "Persistent local inbox"},
        "discord": {"status": "CONFIGURED" if os.getenv("DISCORD_WEBHOOK_URL") else "NOT_CONFIGURED"},
    }


def route_event(event: dict, *, channels: list[str], message: str) -> list[dict]:
    results = []
    base_key = event.get("dedup_key") or event["event_id"]
    for channel in dict.fromkeys(item.lower() for item in channels):
        if channel not in {"app", "discord"}:
            continue
        results.append(queue_delivery(event_id=event["event_id"], channel=channel,
                                      dedup_key=base_key, message=message))
    process_due_deliveries()
    return results


def _post(url: str, payload: dict, headers: dict | None = None) -> None:
    request = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
    with urllib.request.urlopen(request, timeout=8) as response:
        if response.status >= 300:
            raise RuntimeError(f"notification provider returned HTTP {response.status}")


def process_due_deliveries() -> None:
    for item in due_deliveries():
        try:
            if item["channel"] == "app":
                update_delivery(item["delivery_id"], status="SENT")
            elif item["channel"] == "discord":
                webhook = os.getenv("DISCORD_WEBHOOK_URL")
                if not webhook:
                    update_delivery(item["delivery_id"], status="DISABLED", error="Discord is not configured")
                    continue
                _post(webhook, {"content": item["rendered_message"][:2000]})
                update_delivery(item["delivery_id"], status="SENT")
        except (OSError, RuntimeError, urllib.error.URLError) as exc:
            update_delivery(item["delivery_id"], status="RETRY", error=type(exc).__name__)
