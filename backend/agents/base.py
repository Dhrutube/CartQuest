"""
Base store agent — shared config and helpers for all store-specific agents.
Each store agent creates a Browser Use Agent with a task prompt tailored to that store.
"""

import json
from browser_use import Agent, Browser, Tools

# Custom tool so agents can return structured JSON results
tools = Tools()


@tools.action(description="Save a found grocery item with its price info. Call this for each item you find.")
def save_item(
    query: str,
    matched_name: str,
    price: float,
    unit: str = "",
    in_stock: bool = True,
    url: str = "",
) -> str:
    """The agent calls this tool to report each item it finds."""
    result = {
        "query": query,
        "matched_name": matched_name,
        "price": price,
        "unit": unit,
        "in_stock": in_stock,
        "url": url,
    }
    return json.dumps(result)


def build_task_prompt(store_name: str, store_url: str, zip_code: str, items: list[str], extra_instructions: str = "") -> str:
    """Build the natural-language task prompt for a Browser Use agent."""
    items_str = ", ".join(items)
    return f"""You are a grocery price comparison agent for {store_name}.

Your goal: Find the price of each item in this shopping list at {store_name}.

Shopping list: {items_str}
Store zip code: {zip_code}

Steps:
1. Go to {store_url}
2. Set your store location to zip code {zip_code} (look for a store selector, location picker, or delivery/pickup zip code input)
3. For EACH item in the shopping list:
   a. Use the search bar to search for the item
   b. Find the most relevant result (prefer store brand if price is similar)
   c. Call the save_item tool with:
      - query: the original item name from the list
      - matched_name: the full product name you found
      - price: the price as a float (e.g. 3.49)
      - unit: the size/quantity (e.g. "1 dozen", "1 lb", "64 oz")
      - in_stock: true/false
      - url: the product page URL if visible
   d. If an item is not found or out of stock, still call save_item with in_stock=false and price=0
4. After searching all items, you are done.

{extra_instructions}

IMPORTANT:
- Be efficient — don't browse unnecessarily
- Pick the cheapest reasonable option for each item (not bulk/family size unless it's the only option)
- If the site asks about delivery vs pickup, choose pickup
- If a popup or modal appears, dismiss it and continue
"""


def create_browser(agent_id: int, headless: bool = False) -> Browser:
    """Create a Browser instance for an agent."""
    return Browser(
        user_data_dir=f"./tmp-profile-{agent_id}",
        headless=headless,
    )
