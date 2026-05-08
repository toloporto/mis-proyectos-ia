import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Agent {
  id: number;
  name: string;
  role: string;
  llm_model: string;
  system_prompt: string;
  has_code_interpreter: boolean;
  use_rag: boolean;
}

export interface ChatResponse {
  response: string;
  agent: string;
}

export const fetchAgents = async (): Promise<Agent[]> => {
  const response = await api.get('/admin/agents');
  return response.data;
};

export const createAgent = async (agentData: Omit<Agent, 'id'>): Promise<Agent> => {
  const response = await api.post('/admin/agents', agentData);
  return response.data;
};

export const chatWithAgent = async (agentId: number, input: string, sessionId: string = 'default_session'): Promise<ChatResponse> => {
  const response = await api.post(`/agent/${agentId}/chat`, {
    input,
    session_id: sessionId
  });
  return response.data;
};

export default api;

export interface AgentDocument {
  id: number;
  agent_id: number;
  filename: string;
  file_size: number;
  chunk_count: number;
  uploaded_at: string;
}

export const fetchDocuments = async (agentId: number): Promise<AgentDocument[]> => {
  const response = await api.get(`/agent/${agentId}/documents`);
  return response.data;
};

export const uploadDocument = async (agentId: number, file: File): Promise<AgentDocument> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(`/agent/${agentId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const deleteDocument = async (agentId: number, docId: number): Promise<void> => {
  await api.delete(`/agent/${agentId}/documents/${docId}`);
};
