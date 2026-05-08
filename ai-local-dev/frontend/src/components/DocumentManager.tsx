import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Agent, AgentDocument, fetchDocuments, uploadDocument, deleteDocument } from '../api';

interface DocumentManagerProps {
  agent: Agent;
  onBack: () => void;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase();
  if (ext === 'pdf') return '📕';
  if (ext === 'docx' || ext === 'doc') return '📘';
  return '📄';
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({ agent, onBack }) => {
  const [documents, setDocuments] = useState<AgentDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error'; msg: string } | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadDocs = useCallback(async () => {
    try {
      setLoading(true);
      setDocuments(await fetchDocuments(agent.id));
    } catch {
      setStatus({ type: 'error', msg: 'Error cargando documentos' });
    } finally {
      setLoading(false);
    }
  }, [agent.id]);

  useEffect(() => { loadDocs(); }, [loadDocs]);

  const handleUpload = async (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase() || '';
    if (!['pdf', 'docx', 'txt'].includes(ext)) {
      setStatus({ type: 'error', msg: 'Solo se aceptan PDF, DOCX y TXT' });
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      setStatus({ type: 'error', msg: 'El archivo supera el límite de 20 MB' });
      return;
    }
    try {
      setUploading(true);
      setStatus(null);
      const doc = await uploadDocument(agent.id, file);
      setDocuments(prev => [...prev, doc]);
      setStatus({ type: 'success', msg: `✅ "${doc.filename}" indexado — ${doc.chunk_count} fragmentos` });
    } catch (err: any) {
      setStatus({ type: 'error', msg: err.response?.data?.detail || 'Error subiendo el archivo' });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (doc: AgentDocument) => {
    if (!window.confirm(`¿Eliminar "${doc.filename}" de la memoria del agente?`)) return;
    try {
      await deleteDocument(agent.id, doc.id);
      setDocuments(prev => prev.filter(d => d.id !== doc.id));
      setStatus({ type: 'success', msg: `Documento eliminado` });
    } catch {
      setStatus({ type: 'error', msg: 'Error al eliminar el documento' });
    }
  };

  return (
    <div className="doc-manager">
      <div className="doc-header">
        <button className="btn-back" onClick={onBack}>← Volver</button>
        <div>
          <h2>📚 Base de Conocimiento</h2>
          <span className="badge">{agent.name}</span>
        </div>
      </div>

      {status && (
        <div className={`status-banner ${status.type}`}>{status.msg}</div>
      )}

      {/* Zona de carga */}
      <div
        className={`drop-zone ${dragOver ? 'drag-over' : ''} ${uploading ? 'uploading' : ''}`}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={e => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleUpload(f); }}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          style={{ display: 'none' }}
          onChange={e => { const f = e.target.files?.[0]; if (f) handleUpload(f); e.target.value = ''; }}
        />
        {uploading ? (
          <div className="drop-zone-content">
            <div className="spinner"></div>
            <p>Indexando documento...</p>
          </div>
        ) : (
          <div className="drop-zone-content">
            <span className="drop-icon">📂</span>
            <p><strong>Arrastra un archivo aquí</strong> o haz clic para seleccionar</p>
            <small>PDF, DOCX, TXT — máx. 20 MB</small>
          </div>
        )}
      </div>

      {/* Lista de documentos */}
      <div className="doc-list">
        <h3>Documentos indexados ({documents.length})</h3>
        {loading ? (
          <div className="loading">Cargando...</div>
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <p>Aún no hay documentos. Sube el primero para que el agente aprenda.</p>
          </div>
        ) : (
          documents.map(doc => (
            <div key={doc.id} className="doc-item">
              <span className="doc-icon">{fileIcon(doc.filename)}</span>
              <div className="doc-info">
                <span className="doc-name">{doc.filename}</span>
                <span className="doc-meta">
                  {formatBytes(doc.file_size)} · {doc.chunk_count} fragmentos · {new Date(doc.uploaded_at).toLocaleDateString('es-ES')}
                </span>
              </div>
              <button className="btn-delete" onClick={() => handleDelete(doc)}>🗑️</button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
