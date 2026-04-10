import React, { useState, useEffect, useRef } from 'react';
import { documentsApi } from '../services/api';

function DocumentUpload({ onDocumentsUpdated }) {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [ingestingUrl, setIngestingUrl] = useState(false);
  const [message, setMessage] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await documentsApi.list();
      setDocuments(data.documents || []);
      onDocumentsUpdated(data.documents || []);
    } catch (err) {
      showMessage('error', 'Failed to load documents: ' + err.message);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    const results = [];

    for (const file of Array.from(files)) {
      try {
        const result = await documentsApi.upload(file);
        results.push({ success: true, name: file.name, result });
      } catch (err) {
        results.push({ success: false, name: file.name, error: err.message });
      }
    }

    setUploading(false);
    const succeeded = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;

    if (succeeded > 0) {
      showMessage('success', `Successfully uploaded ${succeeded} file(s)${failed > 0 ? `, ${failed} failed` : ''}`);
    } else {
      showMessage('error', `Failed to upload files: ${results.map(r => r.error).join(', ')}`);
    }
    loadDocuments();
  };

  const handleUrlIngest = async () => {
    if (!urlInput.trim()) return;
    setIngestingUrl(true);
    try {
      const result = await documentsApi.ingestUrl(urlInput.trim());
      showMessage('success', `Successfully ingested URL: ${result.chunks_created} chunks created`);
      setUrlInput('');
      loadDocuments();
    } catch (err) {
      showMessage('error', 'Failed to ingest URL: ' + err.message);
    } finally {
      setIngestingUrl(false);
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    try {
      await documentsApi.delete(documentId);
      showMessage('success', 'Document deleted successfully');
      loadDocuments();
    } catch (err) {
      showMessage('error', 'Failed to delete document: ' + err.message);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  return (
    <div>
      <h2 style={{ marginBottom: 20, fontSize: 22, fontWeight: 700 }}>📄 Document Management</h2>

      {message && (
        <div className={`alert alert-${message.type}`}>
          <span>{message.type === 'error' ? '❌' : '✅'}</span>
          {message.text}
        </div>
      )}

      {/* Upload Area */}
      <div className="card">
        <div className="card-title">⬆️ Upload Documents</div>
        <div
          className="drop-zone"
          style={{
            border: `2px dashed ${dragOver ? 'var(--accent-primary)' : 'var(--border-color)'}`,
            borderRadius: 'var(--radius)',
            padding: '40px 20px',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'var(--transition)',
            background: dragOver ? 'rgba(79,142,247,0.05)' : 'transparent',
            marginBottom: 16,
          }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div style={{ fontSize: 40, marginBottom: 12 }}>📁</div>
          <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            {uploading ? (
              <><span className="loading-spinner" style={{ verticalAlign: 'middle', marginRight: 8 }} />Uploading...</>
            ) : (
              <>Drop files here or <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>click to browse</span></>
            )}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>
            Supports: PDF, Word (.doc, .docx), Text (.txt, .md) · Max 50MB
          </div>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt,.md"
          style={{ display: 'none' }}
          onChange={(e) => handleFileUpload(e.target.files)}
        />
      </div>

      {/* URL Ingestion */}
      <div className="card">
        <div className="card-title">🌐 Ingest from URL</div>
        <div style={{ display: 'flex', gap: 10 }}>
          <input
            className="input"
            type="url"
            placeholder="https://example.com/document"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleUrlIngest()}
          />
          <button
            className="btn btn-primary"
            onClick={handleUrlIngest}
            disabled={ingestingUrl || !urlInput.trim()}
          >
            {ingestingUrl ? <span className="loading-spinner" /> : '🌐'}
            {ingestingUrl ? 'Ingesting...' : 'Ingest'}
          </button>
        </div>
      </div>

      {/* Documents List */}
      <div className="card">
        <div className="card-title">
          📚 Knowledge Base
          <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 'auto', fontWeight: 400 }}>
            {documents.length} document{documents.length !== 1 ? 's' : ''}
          </span>
        </div>

        {documents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>📭</div>
            <div>No documents in the knowledge base yet.</div>
            <div style={{ fontSize: 12, marginTop: 8 }}>Upload documents or ingest a URL to get started.</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '12px 14px',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <span style={{ fontSize: 20 }}>
                  {doc.document_type === 'pdf' ? '📕' : doc.document_type === 'word' ? '📘' : doc.document_type === 'web' ? '🌐' : '📄'}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {doc.filename}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                    {doc.chunk_count} chunks · {doc.document_type?.toUpperCase()}
                  </div>
                </div>
                <span className="badge badge-success">indexed</span>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => handleDelete(doc.document_id)}
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default DocumentUpload;
