import React, { useState, useEffect } from 'react';
import './App.css';

interface Agent {
  id: number;
  name: string;
  role: string;
  system_prompt: string;
}

interface Message {
  role: 'user' | 'ia';
  text: string;
}

function App() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  
  // Chat state
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  // Form state
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState('');
  const [newPrompt, setNewPrompt] = useState('');
  const [newModel, setNewModel] = useState('ollama:llama3.2:1b');

  // 1. Cargar agentes al inicio
  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/admin/agents');
      const data = await res.json();
      setAgents(data);
    } catch (e) {
      console.error("Error fetching agents", e);
    }
  };

  const createAgent = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/admin/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newName,
          role: newRole,
          system_prompt: newPrompt,
          llm_model: newModel,
          temperature: 0.7,
          use_rag: false,
          has_code_interpreter: false,
          tools_enabled: []
        })
      });
      if (res.ok) {
        setIsCreating(false);
        setNewName(''); setNewRole(''); setNewPrompt(''); setNewModel('ollama:llama3.2:1b');
        fetchAgents();
      }
    } catch (e) {
      console.error("Error creating agent", e);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !selectedAgent) return;

    const userMsg: Message = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/agent/${selectedAgent.id}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: input, session_id: "react_user" }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Error del servidor");
      const iaMsg: Message = { role: 'ia', text: data.response };
      setMessages(prev => [...prev, iaMsg]);
    } catch (error: any) {
      console.error("Error conectando con el backend:", error);
      setMessages(prev => [...prev, { role: 'ia', text: `Error de conexión: ${error.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="layout">
      {/* SIDEBAR: Panel de Control */}
      <aside className="sidebar">
        <h2>🚀 AI Factory</h2>
        
        <button className="new-agent-btn" onClick={() => {setIsCreating(true); setSelectedAgent(null);}}>
          + Crear Nuevo Agente
        </button>

        <div className="agent-list">
          <h3>Mis Agentes</h3>
          {agents.map(a => (
            <div 
              key={a.id} 
              className={`agent-card ${selectedAgent?.id === a.id ? 'selected' : ''}`}
              onClick={() => {setSelectedAgent(a); setIsCreating(false); setMessages([]);}}
            >
              <h4>{a.name}</h4>
              <p>{a.role} ({a.system_prompt ? 'Configurado' : ''})</p>
            </div>
          ))}
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">
        
        {/* VISTA CREAR AGENTE */}
        {isCreating && (
          <div className="admin-panel">
            <h2>Crear Configuración de Agente</h2>
            <div className="form-group">
              <label>Nombre:</label>
              <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Ej. Dr. Código" />
            </div>
            <div className="form-group">
              <label>Rol:</label>
              <input value={newRole} onChange={e => setNewRole(e.target.value)} placeholder="Ej. Senior Python Developer" />
            </div>
            <div className="form-group">
              <label>Motor de IA (LLM):</label>
              <select value={newModel} onChange={e => setNewModel(e.target.value)} style={{padding: '12px', background: '#161920', color: 'white', border: '1px solid #2a2e38', borderRadius: '6px'}}>
                <option value="ollama:llama3.2:1b">Local: Ollama (llama3.2:1b)</option>
                <option value="gemini-1.5-flash-latest">Nube: Google Gemini 1.5</option>
              </select>
            </div>
            <div className="form-group">
              <label>System Prompt:</label>
              <textarea 
                value={newPrompt} 
                onChange={e => setNewPrompt(e.target.value)} 
                placeholder="Eres un experto en..."
                rows={5}
              />
            </div>
            <button onClick={createAgent} className="save-btn">Guardar Agente</button>
          </div>
        )}

        {/* VISTA CHAT */}
        {selectedAgent && !isCreating && (
          <div className="chat-view">
            <div className="chat-header">
              <h2>{selectedAgent.name} <span className="badge">{selectedAgent.role}</span></h2>
            </div>
            
            <div className="chat-container">
              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.role}`}>
                  <strong>{msg.role === 'user' ? 'Tú' : selectedAgent.name}</strong>
                  <pre className="message-text">{msg.text}</pre>
                </div>
              ))}
              {loading && <p className="loading">Pensando...</p>}
            </div>

            <div className="input-area">
              <input 
                value={input} 
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder={`Habla con ${selectedAgent.name}...`}
              />
              <button onClick={sendMessage} disabled={loading}>Enviar</button>
            </div>
          </div>
        )}

        {!selectedAgent && !isCreating && (
          <div className="empty-state">
            <h2>Selecciona o crea un agente para comenzar.</h2>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
