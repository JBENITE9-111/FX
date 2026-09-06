from fastapi import APIRouter

from services.agents.supervisor import supervisor
from services.agents.sparse_router import route
from services.agents.operations_team import operations_team

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("/runs")
def agent_runs(limit: int = 50):
    return {
        "runs": supervisor.latest(limit=max(1, min(limit, 200)))
    }


@router.get("/team")
def automated_team_status():
    return operations_team.status()


@router.post("/team/run")
def automated_team_run():
    return operations_team.run_once()

@router.get("/route")
def route_experts(tags: str):
    parsed = {
        item.strip().lower()
        for item in tags.split(",")
        if item.strip()
    }

    return {
        "tags": sorted(parsed),
        "selected_experts": route(parsed),
        "risk_note": (
            "Risk is sovereign and remains outside expert voting."
        ),
    }
