from agents.base import build_task_prompt

STORE_NAME = "Vons"
STORE_URL = "https://www.vons.com"

EXTRA_INSTRUCTIONS = """
Store-specific tips for Vons (Albertsons-owned):
- Vons is the local Albertsons brand in San Diego
- Use the search bar to find items
- Look for "Signature SELECT" or "O Organics" as store brands
- Set your store by clicking the location/store selector and entering the zip code
- If prompted to sign in, skip/dismiss and continue as guest
- Look for "Club Price" or sale prices — use the sale price if a club card discount is shown
- Choose "Pickup" if asked about delivery method
"""


def get_task(items: list[str], zip_code: str) -> str:
    return build_task_prompt(STORE_NAME, STORE_URL, zip_code, items, EXTRA_INSTRUCTIONS)
