export default function ResultsDashboard({ results }) {
  if (!results) return null

  const { store_results, best_single_store, optimized_plan, optimized_total, savings, recommendation } = results

  // Find cheapest price per item across all stores
  const cheapestPrices = {}
  for (const store of store_results) {
    for (const item of store.items) {
      const key = item.query.toLowerCase().trim()
      if (item.in_stock && item.price > 0) {
        if (!cheapestPrices[key] || item.price < cheapestPrices[key]) {
          cheapestPrices[key] = item.price
        }
      }
    }
  }

  return (
    <>
      {/* Summary Banner */}
      <div className="card">
        <div className="results-summary">
          {savings > 0 ? (
            <>
              <div className="savings-amount">You save ${savings.toFixed(2)}</div>
              <div className="recommendation">{recommendation}</div>
            </>
          ) : (
            <>
              <div className="savings-amount" style={{ color: 'var(--text)' }}>
                Best deal found
              </div>
              <div className="recommendation">{recommendation}</div>
            </>
          )}
        </div>

        {/* Store Comparison Grid */}
        <h2>📊 Price Comparison</h2>
        <div className="store-comparison">
          {store_results.map(store => {
            const isBest = store.store_name === best_single_store.store_name
            return (
              <div key={store.store_name} className={`store-panel ${isBest ? 'best' : ''}`}>
                <div className="store-name">
                  {store.store_name}
                  {isBest && <span className="best-badge">Cheapest</span>}
                </div>
                {store.error ? (
                  <div className="status error">{store.error}</div>
                ) : (
                  <>
                    <div className="store-total">${store.total.toFixed(2)}</div>
                    <ul className="item-list">
                      {store.items.map((item, i) => {
                        const key = item.query.toLowerCase().trim()
                        const isCheapest = item.in_stock && item.price === cheapestPrices[key]
                        return (
                          <li key={i}>
                            <span className="item-name">
                              {item.query}
                              {item.unit && <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}> ({item.unit})</span>}
                            </span>
                            {item.in_stock ? (
                              <span className={`item-price ${isCheapest ? 'cheapest' : ''}`}>
                                ${item.price.toFixed(2)}
                              </span>
                            ) : (
                              <span className="item-price out-of-stock">Out of stock</span>
                            )}
                          </li>
                        )
                      })}
                    </ul>
                  </>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Optimized Plan */}
      {optimized_plan && optimized_plan.length > 0 && (
        <div className="card">
          <div className="plan-section">
            <h3>🗺️ Your Optimized Shopping Plan</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: 16 }}>
              Total: <strong style={{ color: 'var(--green)' }}>${optimized_total.toFixed(2)}</strong>
              {optimized_plan.length > 1 && ' (including trip costs)'}
            </p>
            {optimized_plan.map((plan, i) => (
              <div key={i} className="plan-store">
                <div className="plan-store-header">
                  <span className="plan-store-name">
                    Stop {i + 1}: {plan.store_name}
                  </span>
                  <span className="plan-store-subtotal">
                    ${plan.subtotal.toFixed(2)}
                  </span>
                </div>
                <ul className="item-list">
                  {plan.items.map((item, j) => (
                    <li key={j}>
                      <span className="item-name">{item.matched_name || item.query}</span>
                      <span className="item-price">${item.price.toFixed(2)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}
