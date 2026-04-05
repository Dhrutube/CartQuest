from agents.base import build_task_prompt

STORE_NAME = "Target"
STORE_URL = "https://www.target.com"

EXTRA_INSTRUCTIONS = """
Store-specific tips for Target:
- Use the search bar at the top to find grocery items
- Look for "Good & Gather" as the store brand
- Set your store location by clicking the store selector (usually top-left) and entering the zip code
- Choose the nearest Target store from the results
- Filter by "Grocery" category if search results include non-food items
- Choose "Order Pickup" if asked about fulfillment method
"""


def get_task(items: list[str], zip_code: str) -> str:
    return build_task_prompt(STORE_NAME, STORE_URL, zip_code, items, EXTRA_INSTRUCTIONS)
