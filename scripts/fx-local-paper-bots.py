from services.local_paper.bot_executor import (
    run,
)

result = run()

print()
print(
    "FX LOCAL PAPER BOT EXECUTOR"
)
print(
    "=" * 60
)

print(
    "Status:",
    result.get(
        "status"
    ),
)

print(
    "Opened:",
    len(
        result.get(
            "opened",
            []
        )
    ),
)

print(
    "Skipped:",
    len(
        result.get(
            "skipped",
            []
        )
    ),
)

print()
