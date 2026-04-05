"""
Optimizer — given price results from all stores, compute:
1. Best single-store option (just go to one place)
2. Optimal multi-store split (cherry-pick cheapest per item, accounting for trip cost)
"""

from models import StoreResult, ItemResult, StoreRecommendation, OptimizeResponse


def optimize(store_results: list[StoreResult], trip_cost: float = 3.00) -> OptimizeResponse:
    """
    Find the cheapest shopping plan.

    Args:
        store_results: Price data from each store agent
        trip_cost: Dollar cost of making an additional store trip (gas, time, etc.)
    """
    # Filter out stores that errored
    valid_stores = [s for s in store_results if s.error is None and s.items]

    if not valid_stores:
        return OptimizeResponse(
            store_results=store_results,
            best_single_store=store_results[0] if store_results else StoreResult(store_name="None", items=[], total=0, error="No results"),
            best_single_store_total=0,
            optimized_plan=[],
            optimized_total=0,
            savings=0,
            recommendation="Could not fetch prices from any store. Please try again.",
        )

    # --- Collect all requested items ---
    all_queries = set()
    for store in valid_stores:
        for item in store.items:
            all_queries.add(item.query.lower().strip())

    # --- Best single store ---
    # Penalize stores with missing/out-of-stock items so $0 doesn't "win"
    def single_store_score(store: StoreResult) -> tuple[int, float]:
        """Sort key: (number of MISSING items, total price of in-stock items).
        Fewer missing items wins first, then cheaper price breaks ties."""
        in_stock_items = [i for i in store.items if i.in_stock and i.price > 0]
        in_stock_queries = {i.query.lower().strip() for i in in_stock_items}
        missing_count = len(all_queries - in_stock_queries)
        in_stock_total = sum(i.price for i in in_stock_items)
        return (missing_count, in_stock_total)

    best_single = min(valid_stores, key=single_store_score)
    # Recalculate total using only in-stock items
    best_single_in_stock = [i for i in best_single.items if i.in_stock and i.price > 0]
    best_single = StoreResult(
        store_name=best_single.store_name,
        items=best_single.items,
        total=round(sum(i.price for i in best_single_in_stock), 2),
    )

    # Fix totals on all store results for display (only count in-stock)
    for store in valid_stores:
        in_stock = [i for i in store.items if i.in_stock and i.price > 0]
        store.total = round(sum(i.price for i in in_stock), 2)

    # Build a lookup: query -> list of (store_name, ItemResult)
    price_map: dict[str, list[tuple[str, ItemResult]]] = {}
    for store in valid_stores:
        for item in store.items:
            key = item.query.lower().strip()
            if key not in price_map:
                price_map[key] = []
            if item.in_stock and item.price > 0:
                price_map[key].append((store.store_name, item))

    # Pick cheapest per item
    optimal_picks: dict[str, list[ItemResult]] = {}  # store_name -> items to buy there
    for query, options in price_map.items():
        if not options:
            continue
        cheapest_store, cheapest_item = min(options, key=lambda x: x[1].price)
        if cheapest_store not in optimal_picks:
            optimal_picks[cheapest_store] = []
        optimal_picks[cheapest_store].append(cheapest_item)

    # Calculate multi-store total including trip costs
    num_stores_in_plan = len(optimal_picks)
    item_total = sum(
        sum(item.price for item in items)
        for items in optimal_picks.values()
    )
    # First store trip is "free" (you're going shopping anyway), extras cost trip_cost each
    extra_trip_cost = max(0, num_stores_in_plan - 1) * trip_cost
    multi_store_total = round(item_total + extra_trip_cost, 2)

    # Build the plan
    optimized_plan = []
    for store_name, items in optimal_picks.items():
        subtotal = round(sum(item.price for item in items), 2)
        optimized_plan.append(StoreRecommendation(
            store_name=store_name,
            items=items,
            subtotal=subtotal,
        ))

    # Decide which plan to recommend
    if multi_store_total < best_single.total:
        savings = round(best_single.total - multi_store_total, 2)
        if num_stores_in_plan > 1:
            store_names = " + ".join(optimal_picks.keys())
            recommendation = (
                f"Split your trip across {store_names} to save ${savings:.2f}! "
                f"(includes ${extra_trip_cost:.2f} estimated cost for {num_stores_in_plan - 1} extra trip(s))"
            )
        else:
            store_name = list(optimal_picks.keys())[0]
            recommendation = f"Shop at {store_name} — it's cheapest for everything on your list!"
    else:
        savings = 0
        recommendation = (
            f"Just go to {best_single.store_name} — it's the best deal at ${best_single.total:.2f}. "
            f"Splitting across stores isn't worth the extra trip."
        )
        # Use single-store plan
        optimized_plan = [StoreRecommendation(
            store_name=best_single.store_name,
            items=best_single.items,
            subtotal=best_single.total,
        )]
        multi_store_total = best_single.total

    # Check for items that are unavailable at ALL stores
    covered_queries = set()
    for options in price_map.values():
        if options:
            covered_queries.add(options[0][1].query.lower().strip())
    unavailable = all_queries - covered_queries
    if unavailable:
        unavailable_names = ", ".join(sorted(unavailable))
        recommendation += f" ⚠️ Not found at any store: {unavailable_names}."

    return OptimizeResponse(
        store_results=store_results,
        best_single_store=best_single,
        best_single_store_total=best_single.total,
        optimized_plan=optimized_plan,
        optimized_total=multi_store_total,
        savings=savings,
        recommendation=recommendation,
    )
