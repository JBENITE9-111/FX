from services.agents.supervisor import supervisor
from services.news.newspaper import refresh

def task(checkpoint):
    checkpoint({"stage": "collecting_sources"})
    result = refresh()
    checkpoint(
        {
            "stage": "ranked",
            "headlines": len(result.get("items", [])),
        }
    )
    return {
        "headlines": len(result.get("items", [])),
        "errors": len(result.get("errors", [])),
    }

run = supervisor.run(
    agent_id="newspaper",
    goal="Refresh and rank the FX Global Newspaper",
    task=task,
)

print("FX Newspaper Agent:", run.status)
print("Result:", run.result)
