from fastapi import APIRouter, HTTPException

from services.brain.trace import brain_trace_store

router = APIRouter(prefix="/api/brain", tags=["brain"])

@router.get("/runs/{run_id}")
def get_run(run_id: str):
    events = brain_trace_store.get_run(run_id)

    if not events:
        raise HTTPException(
            status_code=404,
            detail="Run not found.",
        )

    return {
        "run_id": run_id,
        "display_policy": (
            "structured_evidence_trace_not_hidden_chain_of_thought"
        ),
        "events": events,
    }
