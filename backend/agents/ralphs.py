from agents.base import build_task_prompt

STORE_NAME = "Ralphs"
STORE_URL = "https://www.ralphs.com"

EXTRA_INSTRUCTIONS = """
Store-specific tips for Ralphs (Kroger-owned):
- Ralphs is a Kroger brand — the site works like other Kroger stores
- Use the search bar at the top to find items
- Look for "Kroger" or "Simple Truth" as store brands — usually cheapest
- Set your store by clicking the location selector and entering the zip code
- If prompted to sign in, skip/dismiss and continue as guest
- Look for "Digital Coupon" or sale prices — use the sale price if shown
- Choose "Pickup" if asked about delivery method
"""


def get_task(items: list[str], zip_code: str) -> str:
    return build_task_prompt(STORE_NAME, STORE_URL, zip_code, items, EXTRA_INSTRUCTIONS)