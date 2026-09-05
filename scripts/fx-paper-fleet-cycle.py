from services.agents.supervisor import supervisor
from services.paper_fleet.fleet import run_cycle

def task(checkpoint):
    checkpoint({"stage": "loading_market_data"})
    result = run_cycle()
    checkpoint(
        {
            "stage": "strategy_cycle_complete",
            "strategies": len(result.get("strategies", [])),
        }
    )
    return {
        "strategies": len(result.get("strategies", [])),
        "paper_capital_per_strategy": result.get(
            "paper_capital_per_strategy"
        ),
    }

run = supervisor.run(
    agent_id="paper_strategy_fleet",
    goal="Run every paper strategy, update its $1 virtual account, and persist learning observations",
    task=task,
)

print("FX Paper Fleet Agent:", run.status)
print("Result:", run.result)
