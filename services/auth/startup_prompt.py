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
    reuse_fx_tab = r'''
tell application "Google Chrome"
    if it is running then
        repeat with window_index from 1 to count of windows
            set browser_window to window window_index
            repeat with tab_index from 1 to count of tabs of browser_window
                set browser_tab to tab tab_index of browser_window
                if URL of browser_tab starts with "http://127.0.0.1:8000/" then
                    set URL of browser_tab to "http://127.0.0.1:8000/security"
                    set active tab index of browser_window to tab_index
                    set index of browser_window to 1
                    activate
                    return
                end if
            end repeat
        end repeat
    end if
end tell
open location "http://127.0.0.1:8000/security"
'''
    browser = await asyncio.create_subprocess_exec(
        "/usr/bin/osascript",
        "-e",
        reuse_fx_tab,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await browser.wait()


def schedule_totp_prompt() -> None:
    task = asyncio.create_task(_prompt_for_totp())
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
