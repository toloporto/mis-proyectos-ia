import React, { useState, useRef, useEffect } from 'react';
import { Agent, chatWithAgent } from '../api';

interface ChatInterfaceProps {
  agent: Agent;
  onBack: () => void;
}

interface Message {
  role: 'user' | 'agent';
  content: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ agent, onBack }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    
    try {
      setLoading(true);
      const data = await chatWithAgent(agent.id, userMessage);
      setMessages(prev => [...prev, { role: 'agent', content: data.response }]);
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'agent', content: `Error: ${err.message || 'No se pudo conectar con el agente'}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button className="btn-back" onClick={onBack}>← Volver</button>
        <div className="chat-header-info">
          <h2>{agent.name}</h2>
          <span className="badge">{agent.role}</span>
        </div>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <div className="bot-icon">🤖</div>
            <p>Comienza una conversación con {agent.name}</p>
            <small>Modelo: {agent.llm_model}</small>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className="message-bubble">
                {msg.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="message-wrapper agent">
            <div className="message-bubble loading-bubble">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-area" onSubmit={handleSend}>
        <input 
          type="text" 
          value={input} 
          onChange={e => setInput(e.target.value)} 
          placeholder={`Envía un mensaje a ${agent.name}...`}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} className="btn-send">
          ➤
        </button>
      </form>
    </div>
  );
};
