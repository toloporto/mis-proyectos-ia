import React, { useState } from 'react';
import { AgentList } from './components/AgentList';
import { CreateAgentForm } from './components/CreateAgentForm';
import { ChatInterface } from './components/ChatInterface';
import { DocumentManager } from './components/DocumentManager';
import { Agent } from './api';

function App() {
  const [currentView, setCurrentView] = useState<'list' | 'create' | 'chat' | 'documents'>('list');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(false);

  const handleCreateAgent = () => {
    setCurrentView('list');
    setRefreshTrigger(!refreshTrigger);
  };

  const handleManageDocs = (agent: Agent) => {
    setSelectedAgent(agent);
    setCurrentView('documents');
  };

  const handleSelectAgent = (agent: Agent) => {
    setSelectedAgent(agent);
    setCurrentView('chat');
  };

  return (
    <div className="app-layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <span className="logo-icon">🤖</span>
          <h1>AI Agent Factory</h1>
        </div>
        <div className="navbar-actions">
          {currentView === 'list' && (
            <button className="btn btn-primary" onClick={() => setCurrentView('create')}>
              + Crear Nuevo Agente
            </button>
          )}
        </div>
      </nav>

      <main className="main-content">
        {currentView === 'list' && (
          <AgentList 
            onSelectAgent={handleSelectAgent}
            onManageDocs={handleManageDocs}
            onRefresh={refreshTrigger} 
          />
        )}
        
        {currentView === 'create' && (
          <CreateAgentForm 
            onAgentCreated={handleCreateAgent}
            onCancel={() => setCurrentView('list')}
          />
        )}
        
        {currentView === 'chat' && selectedAgent && (
          <ChatInterface 
            agent={selectedAgent}
            onBack={() => {
              setSelectedAgent(null);
              setCurrentView('list');
            }}
          />
        )}
        {currentView === 'documents' && selectedAgent && (
          <DocumentManager
            agent={selectedAgent}
            onBack={() => { setSelectedAgent(null); setCurrentView('list'); }}
          />
        )}
      </main>
    </div>
  );
}

export default App;
