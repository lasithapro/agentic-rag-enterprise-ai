import React from 'react';

const navItems = [
  { id: 'query', icon: '🔍', label: 'Query Assistant' },
  { id: 'documents', icon: '📄', label: 'Documents' },
  { id: 'reports', icon: '📊', label: 'Reports' },
];

function Sidebar({ activeTab, onTabChange, apiStatus, documentCount }) {
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <span className="sidebar-logo-icon">⚡</span>
        <div className="sidebar-logo-text">
          <h2>AGENTIC RAG</h2>
          <p>Enterprise AI Platform</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <div
            key={item.id}
            className={`sidebar-nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => onTabChange(item.id)}
          >
            <span className="sidebar-nav-icon">{item.icon}</span>
            <span>{item.label}</span>
            {item.id === 'documents' && documentCount > 0 && (
              <span className="sidebar-nav-badge">{documentCount}</span>
            )}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <span style={{
            width: 8, height: 8, borderRadius: '50%',
            background: apiStatus === 'healthy' ? 'var(--accent-success)' : apiStatus === 'unhealthy' ? 'var(--accent-danger)' : 'var(--text-muted)',
            display: 'inline-block'
          }}></span>
          <span>{apiStatus === 'healthy' ? 'System Online' : apiStatus === 'unhealthy' ? 'System Offline' : 'Connecting...'}</span>
        </div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 6 }}>
          v1.0.0 · Multi-Agent RAG
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
