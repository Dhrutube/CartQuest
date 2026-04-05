from agents.base import build_task_prompt

STORE_NAME = "Walmart"
STORE_URL = "https://www.walmart.com/grocery"

EXTRA_INSTRUCTIONS = """
Store-specific tips for Walmart:
- The grocery section is at walmart.com/grocery
- Look for "Great Value" as the store brand — it's usually cheapest
- Set your store by clicking the location icon or "How do you want your items?" and entering the zip code
- Choose "Pickup" if asked about delivery method
- Prices may show as "current price" — use that number
"""


def get_task(items: list[str], zip_code: str) -> str:
    return build_task_prompt(STORE_NAME, STORE_URL, zip_code, items, EXTRA_INSTRUCTIONS)
