"""
CartQuest API — FastAPI server with SSE streaming for real-time agent updates.
"""

import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models import OptimizeRequest, AgentEvent
from orchestrator import run_all_agents
from optimizer import optimize

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CartQuest", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_llm():
    """
    Initialize the LLM for Browser Use agents.
    Tries Browser Use → Anthropic → OpenAI in order of preference.
    """
    if os.getenv("BROWSER_USE_API_KEY"):
        from browser_use import ChatBrowserUse
        return ChatBrowserUse()

    if os.getenv("ANTHROPIC_API_KEY"):
        from browser_use import ChatAnthropic
        return ChatAnthropic(model="claude-sonnet-4-6")

    if os.getenv("OPENAI_API_KEY"):
        from browser_use import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini")

    raise RuntimeError(
        "No LLM API key found. Set BROWSER_USE_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY in .env"
    )


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "CartQuest"}


@app.post("/api/optimize")
async def optimize_endpoint(request: OptimizeRequest):
    """
    Non-streaming endpoint — kicks off agents, waits for all results, returns final optimization.
    Good for testing; the SSE endpoint is better for demos.
    """
    llm = get_llm()
    items = [item.strip() for item in request.items if item.strip()]

    store_results = await run_all_agents(
        items=items,
        zip_code=request.zip_code,
        llm=llm,
        headless=True,
    )

    result = optimize(store_results, trip_cost=request.trip_cost)
    return result


@app.post("/api/optimize/stream")
async def optimize_stream(request: OptimizeRequest):
    """
    SSE streaming endpoint — sends real-time agent updates to the frontend.
    This is the main endpoint for the demo UI.
    """
    llm = get_llm()
    items = [item.strip() for item in request.items if item.strip()]
    event_queue: asyncio.Queue = asyncio.Queue()

    async def run_agents_background():
        """Background task that runs agents and puts events in the queue."""
        try:
            store_results = await run_all_agents(
                items=items,
                zip_code=request.zip_code,
                llm=llm,
                headless=False,  # show browsers for demo!
                event_queue=event_queue,
            )
            result = optimize(store_results, trip_cost=request.trip_cost)
            await event_queue.put(AgentEvent(
                event=AgentEvent.EventType.OPTIMIZATION_DONE,
                store="all",
                data=result.model_dump(),
            ))
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            await event_queue.put(AgentEvent(
                event=AgentEvent.EventType.AGENT_ERROR,
                store="all",
                data={"error": str(e)},
            ))
        finally:
            await event_queue.put(None)  # sentinel to close stream

    async def event_generator():
        """Yield SSE events from the queue."""
        task = asyncio.create_task(run_agents_background())
        try:
            while True:
                event = await event_queue.get()
                if event is None:
                    break
                yield f"data: {event.model_dump_json()}\n\n"
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
