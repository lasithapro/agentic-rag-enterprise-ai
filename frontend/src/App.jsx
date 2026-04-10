import React, { useState, useEffect } from 'react';
import DocumentUpload from './components/DocumentUpload';
import QueryInterface from './components/QueryInterface';
import ReportViewer from './components/ReportViewer';
import Sidebar from './components/Sidebar';
import { healthApi } from './services/api';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('query');
  const [documents, setDocuments] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      await healthApi.check();
      setApiStatus('healthy');
    } catch (error) {
      setApiStatus('unhealthy');
    }
  };

  const handleDocumentsUpdated = (updatedDocs) => {
    setDocuments(updatedDocs);
  };

  const handleReportGenerated = (report) => {
    setSelectedReport(report);
    setActiveTab('reports');
  };

  return (
    <div className="app">
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        apiStatus={apiStatus}
        documentCount={documents.length}
      />
      <main className="main-content">
        <header className="app-header">
          <div className="header-content">
            <div className="header-title">
              <span className="header-icon">🤖</span>
              <div>
                <h1>Agentic RAG Enterprise AI</h1>
                <p className="header-subtitle">Multi-Agent Document Analysis Platform</p>
              </div>
            </div>
            <div className={`api-status api-status--${apiStatus}`}>
              <span className="status-dot"></span>
              {apiStatus === 'healthy' ? 'API Connected' : apiStatus === 'checking' ? 'Connecting...' : 'API Offline'}
            </div>
          </div>
        </header>

        <div className="content-area">
          {activeTab === 'documents' && (
            <DocumentUpload
              onDocumentsUpdated={handleDocumentsUpdated}
            />
          )}
          {activeTab === 'query' && (
            <QueryInterface
              documents={documents}
              onReportGenerated={handleReportGenerated}
            />
          )}
          {activeTab === 'reports' && (
            <ReportViewer
              documents={documents}
              selectedReport={selectedReport}
              onReportCleared={() => setSelectedReport(null)}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
