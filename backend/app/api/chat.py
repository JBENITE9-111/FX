from fastapi import (
    APIRouter,
)

from pydantic import (
    BaseModel,
)

from backend.app.services.llm.router import (
    FXLLMRouter,
)

from backend.app.services.research.grounded_answer import (
    grounded_answer,
)


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


class ChatRequest(
    BaseModel
):

    message: str


@router.post("")
async def chat(
    request: ChatRequest,
):

    try:

        real_answer = (
            grounded_answer(
                request.message
            )
        )

        if real_answer:

            return {
                "provider": (
                    "FX deterministic research engine"
                ),
                "model": (
                    "London Strategic Edge + Model Council"
                ),
                "answer": (
                    real_answer
                ),
            }

    except Exception:

        pass

    llm = FXLLMRouter()

    return await llm.reason(
        request.message
    )
