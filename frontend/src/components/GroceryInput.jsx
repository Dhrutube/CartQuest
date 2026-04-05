import { useState } from 'react'

const DEFAULT_LIST = `eggs
chicken breast
oat milk
rice
bananas
greek yogurt
bread
spinach`

export default function GroceryInput({ onSubmit, isLoading }) {
  const [items, setItems] = useState(DEFAULT_LIST)
  const [zipCode, setZipCode] = useState('92092')
  const [tripCost, setTripCost] = useState('0.00')

  const handleSubmit = () => {
    const itemList = items
      .split('\n')
      .map(s => s.trim())
      .filter(Boolean)

    if (itemList.length === 0) return

    onSubmit({
      items: itemList,
      zip_code: zipCode,
      trip_cost: parseFloat(tripCost) || 3.0,
    })
  }

  return (
    <div className="card">
      <h2>🧾 Your Grocery List</h2>

      <div className="input-group">
        <label>Items (one per line)</label>
        <textarea
          value={items}
          onChange={e => setItems(e.target.value)}
          placeholder="eggs&#10;chicken breast&#10;oat milk&#10;..."
          disabled={isLoading}
        />
      </div>

      <div className="input-row">
        <div className="input-group">
          <label>Zip Code</label>
          <input
            type="text"
            value={zipCode}
            onChange={e => setZipCode(e.target.value)}
            placeholder="2"
            disabled={isLoading}
          />
        </div>
        <div className="input-group">
          <label>Trip Cost ($)</label>
          <input
            type="number"
            value={tripCost}
            onChange={e => setTripCost(e.target.value)}
            placeholder="3.00"
            step="0.50"
            min="0"
            disabled={isLoading}
          />
        </div>
      </div>

      <button
        className="btn-primary"
        onClick={handleSubmit}
        disabled={isLoading || !items.trim()}
      >
        {isLoading ? (
          <>
            <span className="spinner" />
            Agents shopping...
          </>
        ) : (
          '🛒 Find the Best Prices'
        )}
      </button>
    </div>
  )
}
