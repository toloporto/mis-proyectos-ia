import React, { useState } from 'react';
import { createAgent } from '../api';

interface CreateAgentFormProps {
  onAgentCreated: () => void;
  onCancel: () => void;
}

export const CreateAgentForm: React.FC<CreateAgentFormProps> = ({ onAgentCreated, onCancel }) => {
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [llmModel, setLlmModel] = useState('ollama:qwen2.5:7b');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [useRag, setUseRag] = useState(false);
  const [hasCodeInterpreter, setHasCodeInterpreter] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      await createAgent({
        name,
        role,
        llm_model: llmModel,
        system_prompt: systemPrompt,
        use_rag: useRag,
        has_code_interpreter: hasCodeInterpreter
      });
      onAgentCreated();
    } catch (err: any) {
      setError(err.message || 'Error al crear el agente');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Crear Nuevo Agente</h2>
      {error && <div className="error-banner">{error}</div>}
      <form onSubmit={handleSubmit} className="agent-form">
        <div className="form-group">
          <label>Nombre del Agente</label>
          <input 
            type="text" 
            value={name} 
            onChange={e => setName(e.target.value)} 
            placeholder="Ej. Asistente Clínico"
            required 
          />
        </div>
        
        <div className="form-group">
          <label>Rol</label>
          <input 
            type="text" 
            value={role} 
            onChange={e => setRole(e.target.value)} 
            placeholder="Ej. Médico Especialista"
            required 
          />
        </div>

        <div className="form-group">
          <label>Modelo LLM</label>
          <select value={llmModel} onChange={e => setLlmModel(e.target.value)}>
            <option value="ollama:qwen2.5:7b">Local - Qwen 2.5 7B</option>
            <option value="ollama:llama3.2:1b">Local - Llama 3.2 1B</option>
            <option value="gemini-1.5-pro">Cloud - Gemini 1.5 Pro</option>
            <option value="gemini-1.5-flash">Cloud - Gemini 1.5 Flash</option>
          </select>
        </div>

        <div className="form-group">
          <label>System Prompt (Instrucciones base)</label>
          <textarea 
            value={systemPrompt} 
            onChange={e => setSystemPrompt(e.target.value)} 
            placeholder="Eres un asistente especializado en..."
            rows={5}
            required 
          />
        </div>

        <div className="form-group-checkbox">
          <label className="checkbox-label">
            <input 
              type="checkbox" 
              checked={useRag} 
              onChange={e => setUseRag(e.target.checked)} 
            />
            Habilitar RAG Clínico (Qdrant)
          </label>
        </div>

        <div className="form-group-checkbox">
          <label className="checkbox-label">
            <input 
              type="checkbox" 
              checked={hasCodeInterpreter} 
              onChange={e => setHasCodeInterpreter(e.target.checked)} 
            />
            Habilitar Code Interpreter
          </label>
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={loading}>
            Cancelar
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creando...' : 'Crear Agente'}
          </button>
        </div>
      </form>
    </div>
  );
};
