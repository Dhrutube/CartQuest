import { useState, useCallback } from 'react'
import GroceryInput from './components/GroceryInput'
import AgentStatus from './components/AgentStatus'
import ResultsDashboard from './components/ResultsDashboard'

const STORES = ["Ralphs", "Target", "Trader Joe's"]

export default function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [agents, setAgents] = useState(null)
  const [results, setResults] = useState(null)

  const handleSubmit = useCallback(async (request) => {
    setIsLoading(true)
    setResults(null)

    // Initialize agent status
    const initialAgents = {}
    STORES.forEach(store => {
      initialAgents[store] = { status: 'idle', itemsFound: 0, error: null }
    })
    setAgents(initialAgents)

    try {
      const response = await fetch('/api/optimize/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))
            handleSSEEvent(event)
          } catch (e) {
            console.warn('Failed to parse SSE event:', e)
          }
        }
      }
    } catch (err) {
      console.error('Optimization failed:', err)
      // Update all agents to error state
      setAgents(prev => {
        const updated = { ...prev }
        for (const store of STORES) {
          if (updated[store]?.status !== 'agent_done') {
            updated[store] = { ...updated[store], status: 'agent_error', error: err.message }
          }
        }
        return updated
      })
    } finally {
      setIsLoading(false)
    }
  }, [])

  const handleSSEEvent = (event) => {
    switch (event.event) {
      case 'agent_start':
      case 'agent_searching':
        setAgents(prev => ({
          ...prev,
          [event.store]: {
            ...prev?.[event.store],
            status: event.event,
          },
        }))
        break

      case 'item_found':
        setAgents(prev => ({
          ...prev,
          [event.store]: {
            ...prev?.[event.store],
            itemsFound: (prev?.[event.store]?.itemsFound || 0) + 1,
          },
        }))
        break

      case 'agent_done':
        setAgents(prev => ({
          ...prev,
          [event.store]: {
            ...prev?.[event.store],
            status: 'agent_done',
            itemsFound: event.data?.items_found || prev?.[event.store]?.itemsFound || 0,
          },
        }))
        break

      case 'agent_error':
        setAgents(prev => ({
          ...prev,
          [event.store]: {
            ...prev?.[event.store],
            status: 'agent_error',
            error: event.data?.error || 'Unknown error',
          },
        }))
        break

      case 'optimization_done':
        setResults(event.data)
        break
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>
          <span className="emoji">🛒</span> CartQuest
        </h1>
        <p>
          AI agents shop every store near you — so you don't have to.
        </p>
      </header>

      <GroceryInput onSubmit={handleSubmit} isLoading={isLoading} />
      <AgentStatus agents={agents} />
      <ResultsDashboard results={results} />
    </div>
  )
}
