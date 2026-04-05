"""
Orchestrator — spawns one Browser Use agent per store, runs them in parallel,
collects structured results, and feeds them to the optimizer.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from browser_use import Agent, Browser

from agents.base import tools, create_browser
from agents import ralphs, target, traderjoes

from models import StoreResult, ItemResult, AgentEvent

logger = logging.getLogger(__name__)

# Registry of supported stores
STORES = {
    "Ralphs": ralphs,
    "Target": target,
    "Trader Joe's": traderjoes,
}


async def run_store_agent(
    store_name: str,
    store_module,
    items: list[str],
    zip_code: str,
    llm,
    agent_id: int,
    headless: bool = False,
    event_queue: asyncio.Queue | None = None,
) -> StoreResult:
    """Run a single store agent and return structured results."""

    browser = create_browser(agent_id, headless=headless)
    task = store_module.get_task(items, zip_code)

    if event_queue:
        await event_queue.put(AgentEvent(
            event=AgentEvent.EventType.AGENT_START,
            store=store_name,
            data={"items_count": len(items)},
        ))

    try:
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            tools=tools,
        )
        result = await agent.run()

        # Parse the save_item tool calls from the agent's action history
        found_items = _extract_items_from_result(result, store_name)

        if event_queue:
            await event_queue.put(AgentEvent(
                event=AgentEvent.EventType.AGENT_DONE,
                store=store_name,
                data={"items_found": len(found_items)},
            ))

        total = sum(item.price for item in found_items if item.in_stock)

        return StoreResult(
            store_name=store_name,
            items=found_items,
            total=round(total, 2),
        )

    except Exception as e:
        logger.error(f"Agent for {store_name} failed: {e}")
        if event_queue:
            await event_queue.put(AgentEvent(
                event=AgentEvent.EventType.AGENT_ERROR,
                store=store_name,
                data={"error": str(e)},
            ))
        return StoreResult(
            store_name=store_name,
            items=[],
            total=0,
            error=str(e),
        )
    finally:
        try:
            await browser.close()
        except AttributeError:
            pass  # Browser Use handles cleanup internally


def _extract_items_from_result(result, store_name: str) -> list[ItemResult]:
    """
    Extract ItemResult objects from the agent's run result.

    Browser Use agents return results that include tool call outputs.
    We look for our save_item tool calls and parse their JSON output.
    """
    items = []

    # The result object contains the history of actions.
    # We look for tool results from our save_item tool.
    try:
        for history_item in result.history:
            if hasattr(history_item, "result") and history_item.result:
                for action_result in history_item.result:
                    if hasattr(action_result, "extracted_content") and action_result.extracted_content:
                        try:
                            data = json.loads(action_result.extracted_content)
                            if "query" in data and "price" in data:
                                items.append(ItemResult(**data))
                        except (json.JSONDecodeError, TypeError):
                            continue
    except Exception as e:
        logger.warning(f"Could not parse results for {store_name}: {e}")

    return items


async def run_all_agents(
    items: list[str],
    zip_code: str,
    llm,
    headless: bool = False,
    event_queue: asyncio.Queue | None = None,
) -> list[StoreResult]:
    """Run all store agents in parallel and return results."""

    tasks = []
    for i, (store_name, store_module) in enumerate(STORES.items()):
        task = run_store_agent(
            store_name=store_name,
            store_module=store_module,
            items=items,
            zip_code=zip_code,
            llm=llm,
            agent_id=i,
            headless=headless,
            event_queue=event_queue,
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Convert any exceptions to error StoreResults
    store_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            store_name = list(STORES.keys())[i]
            store_results.append(StoreResult(
                store_name=store_name,
                items=[],
                total=0,
                error=str(result),
            ))
        else:
            store_results.append(result)

    return store_results
