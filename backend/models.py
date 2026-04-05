from pydantic import BaseModel
from enum import Enum


class OptimizeRequest(BaseModel):
    items: list[str]
    zip_code: str = "92093"
    trip_cost: float = 3.00  # dollar cost of an extra store trip (gas + time)


class ItemResult(BaseModel):
    query: str            # what the user asked for, e.g. "eggs"
    matched_name: str     # what the agent found, e.g. "Great Value Large Eggs, 12 ct"
    price: float
    unit: str | None = None  # e.g. "12 ct", "1 gal"
    in_stock: bool = True
    url: str | None = None


class StoreResult(BaseModel):
    store_name: str
    items: list[ItemResult]
    total: float
    error: str | None = None


class StoreRecommendation(BaseModel):
    store_name: str
    items: list[ItemResult]
    subtotal: float


class OptimizeResponse(BaseModel):
    store_results: list[StoreResult]
    best_single_store: StoreResult
    best_single_store_total: float
    optimized_plan: list[StoreRecommendation]
    optimized_total: float
    savings: float
    recommendation: str  # human-readable summary


class AgentEvent(BaseModel):
    """SSE event sent to frontend during agent execution."""
    class EventType(str, Enum):
        AGENT_START = "agent_start"
        AGENT_SEARCHING = "agent_searching"
        ITEM_FOUND = "item_found"
        AGENT_DONE = "agent_done"
        AGENT_ERROR = "agent_error"
        OPTIMIZATION_DONE = "optimization_done"

    event: EventType
    store: str
    data: dict = {}
