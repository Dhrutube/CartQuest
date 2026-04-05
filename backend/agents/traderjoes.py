from agents.base import build_task_prompt

STORE_NAME = "Trader Joe's"
STORE_URL = "https://www.traderjoes.com"

EXTRA_INSTRUCTIONS = """
Store-specific tips for Trader Joe's:
- Trader Joe's has a limited online product listing — not all items have prices on the website
- Use the search bar or browse by category
- All products are Trader Joe's store brand
- Prices on the website may not always be listed — if a price is not shown, search for "[item name] trader joe's price" on Google as a fallback
- Trader Joe's does NOT offer online ordering or pickup — this is just for price comparison
- If the site doesn't show a price for an item, call save_item with price=0 and in_stock=false
"""


def get_task(items: list[str], zip_code: str) -> str:
    return build_task_prompt(STORE_NAME, STORE_URL, zip_code, items, EXTRA_INSTRUCTIONS)