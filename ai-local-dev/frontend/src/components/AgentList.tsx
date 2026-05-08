import React, { useEffect, useState } from 'react';
import { Agent, fetchAgents } from '../api';

interface AgentListProps {
  onSelectAgent: (agent: Agent) => void;
  onManageDocs: (agent: Agent) => void;
  onRefresh?: boolean;
}

export const AgentList: React.FC<AgentListProps> = ({ onSelectAgent, onManageDocs, onRefresh }) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAgents();
  }, [onRefresh]);

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAgents();
      setAgents(data);
    } catch (err: any) {
      setError(err.message || 'Error cargando agentes');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Cargando agentes...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="agent-list">
      <h2>Mis Agentes</h2>
      {agents.length === 0 ? (
        <p className="empty-state">No hay agentes creados. ¡Crea uno nuevo!</p>
      ) : (
        <div className="grid">
          {agents.map((agent) => (
            <div key={agent.id} className="card agent-card" onClick={() => onSelectAgent(agent)}>
              <div className="card-header">
                <h3>{agent.name}</h3>
                <span className="badge">{agent.role}</span>
              </div>
              <p className="model-info">Modelo: {agent.llm_model}</p>
              <div className="features">
                {agent.use_rag && <span className="feature">RAG</span>}
                {agent.has_code_interpreter && <span className="feature">Code Interpreter</span>}
              </div>
              <div className="card-actions" onClick={e => e.stopPropagation()}>
                <button className="btn btn-primary btn-sm" onClick={() => onSelectAgent(agent)}>💬 Chatear</button>
                {agent.use_rag && (
                  <button className="btn btn-secondary btn-sm" onClick={() => onManageDocs(agent)}>📚 Documentos</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
