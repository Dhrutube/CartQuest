const STORE_EMOJIS = {
  Ralphs: '🔵',
  Target: '🔴',
  "Trader Joe's": '🌺',
}

const STATUS_LABELS = {
  idle: 'Waiting...',
  agent_start: 'Launching browser...',
  agent_searching: 'Searching items...',
  agent_done: 'Done!',
  agent_error: 'Error',
}

export default function AgentStatus({ agents }) {
  if (!agents || Object.keys(agents).length === 0) return null

  return (
    <div className="card">
      <h2>🤖 Agent Status</h2>
      <div className="agent-grid">
        {Object.entries(agents).map(([store, agent]) => {
          const statusClass =
            agent.status === 'agent_done' ? 'done'
            : agent.status === 'agent_error' ? 'error'
            : agent.status !== 'idle' ? 'running'
            : ''

          return (
            <div key={store} className={`agent-card ${statusClass}`}>
              <h3>
                {STORE_EMOJIS[store] || '🏪'} {store}
              </h3>
              <div className={`status ${statusClass}`}>
                {STATUS_LABELS[agent.status] || agent.status}
              </div>
              {agent.itemsFound > 0 && (
                <div className="items-found">
                  {agent.itemsFound} item{agent.itemsFound !== 1 ? 's' : ''} found
                </div>
              )}
              {agent.error && (
                <div className="status error" style={{ marginTop: 6, fontSize: '0.8rem' }}>
                  {agent.error}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
