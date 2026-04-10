import React, { useState, useRef, useEffect } from 'react';
import { queryApi } from '../services/api';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';

function QueryInterface({ documents, onReportGenerated }) {
  const [sessionId] = useState(() => uuidv4());
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDocIds, setSelectedDocIds] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleQuery = async () => {
    if (!input.trim() || loading) return;
    const userMessage = input.trim();
    setInput('');
    setError(null);

    setMessages(prev => [...prev, {
      id: uuidv4(), role: 'user', content: userMessage, timestamp: Date.now()
    }]);

    setLoading(true);
    try {
      const response = await queryApi.query(
        userMessage,
        sessionId,
        5,
        selectedDocIds.length > 0 ? selectedDocIds : null
      );

      setMessages(prev => [...prev, {
        id: uuidv4(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence_score,
        reasoning: response.reasoning_steps,
        processingTime: response.processing_time_ms,
        timestamp: Date.now(),
      }]);
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, {
        id: uuidv4(), role: 'error', content: err.message, timestamp: Date.now()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = async () => {
    setMessages([]);
    try { await queryApi.clearMemory(sessionId); } catch (e) {}
  };

  const exampleQueries = [
    "Summarize the key compliance requirements",
    "What are the main risks identified?",
    "List the action items and recommendations",
    "What policies are mentioned in the documents?",
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700 }}>🔍 Query Assistant</h2>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          {documents.length > 0 && (
            <select
              className="input"
              style={{ width: 200 }}
              multiple={false}
              onChange={(e) => {
                const val = e.target.value;
                setSelectedDocIds(val ? [val] : []);
              }}
            >
              <option value="">All Documents</option>
              {documents.map(doc => (
                <option key={doc.document_id} value={doc.document_id}>
                  {doc.filename && doc.filename.length > 30 ? doc.filename.substring(0, 30) + '...' : doc.filename}
                </option>
              ))}
            </select>
          )}
          {messages.length > 0 && (
            <button className="btn btn-secondary btn-sm" onClick={clearConversation}>
              🗑️ Clear
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1, overflowY: 'auto',
        background: 'var(--bg-secondary)',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border-color)',
        padding: 16,
        marginBottom: 16,
        minHeight: 300,
      }}>
        {messages.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 20 }}>
            <div style={{ fontSize: 48 }}>🤖</div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Ready to assist</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
                {documents.length === 0
                  ? 'Upload documents first to enable intelligent Q&A'
                  : `Analyzing ${documents.length} document(s) in your knowledge base`}
              </div>
              {documents.length > 0 && (
                <div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 10 }}>Try asking:</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                    {exampleQueries.map((q, i) => (
                      <button
                        key={i}
                        className="btn btn-secondary btn-sm"
                        onClick={() => setInput(q)}
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {messages.map((msg) => (
              <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{
                  maxWidth: '80%',
                  padding: '12px 16px',
                  borderRadius: msg.role === 'user' ? '12px 12px 4px 12px' : '12px 12px 12px 4px',
                  background: msg.role === 'user'
                    ? 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))'
                    : msg.role === 'error'
                    ? 'rgba(239,83,80,0.1)'
                    : 'var(--bg-card)',
                  border: msg.role === 'assistant' ? '1px solid var(--border-color)' : 'none',
                  fontSize: 14,
                  lineHeight: 1.6,
                }}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    <span>{msg.content}</span>
                  )}
                </div>

                {msg.role === 'assistant' && (
                  <div style={{ display: 'flex', gap: 12, marginTop: 6, padding: '0 4px', flexWrap: 'wrap' }}>
                    {msg.confidence !== undefined && (
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        Confidence: {Math.round(msg.confidence * 100)}%
                      </span>
                    )}
                    {msg.processingTime && (
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        {Math.round(msg.processingTime)}ms
                      </span>
                    )}
                    {msg.sources && msg.sources.length > 0 && (
                      <span style={{ fontSize: 11, color: 'var(--accent-primary)' }}>
                        📎 {msg.sources.length} source{msg.sources.length !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                )}

                {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                  <details style={{ marginTop: 8, maxWidth: '80%' }}>
                    <summary style={{ fontSize: 12, color: 'var(--text-muted)', cursor: 'pointer' }}>
                      View sources ({msg.sources.length})
                    </summary>
                    <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {msg.sources.map((src, i) => (
                        <div key={i} style={{
                          background: 'var(--bg-tertiary)',
                          border: '1px solid var(--border-color)',
                          borderRadius: 6,
                          padding: '8px 12px',
                          fontSize: 12,
                        }}>
                          <div style={{ fontWeight: 600, marginBottom: 4, color: 'var(--accent-primary)' }}>
                            {src.filename} {src.page_number ? `(p.${src.page_number})` : ''}
                          </div>
                          <div style={{ color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                            {src.content?.substring(0, 200)}...
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            ))}

            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-muted)', fontSize: 13 }}>
                <span className="loading-spinner" />
                Agents are analyzing your query...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: 10 }}>
        <input
          className="input"
          type="text"
          placeholder={documents.length === 0 ? "Upload documents to start querying..." : "Ask a question about your documents..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleQuery()}
          disabled={loading || documents.length === 0}
        />
        <button
          className="btn btn-primary"
          onClick={handleQuery}
          disabled={loading || !input.trim() || documents.length === 0}
        >
          {loading ? <span className="loading-spinner" /> : '→'}
          Send
        </button>
      </div>
    </div>
  );
}

export default QueryInterface;
