from __future__ import annotations

import asyncio


_tasks: set[asyncio.Task] = set()


async def _prompt_for_totp() -> None:
    await asyncio.sleep(1)
    notification = await asyncio.create_subprocess_exec(
        "/usr/bin/osascript",
        "-e",
        'display notification "Enter your Google Authenticator code to start scanners, learning and favorite monitoring." with title "FX is locked" sound name "Glass"',
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await notification.wait()
    browser = await asyncio.create_subprocess_exec(
        "/usr/bin/open",
        "http://127.0.0.1:8000/security",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await browser.wait()


def schedule_totp_prompt() -> None:
    task = asyncio.create_task(_prompt_for_totp())
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
