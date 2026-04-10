import React, { useState } from 'react';
import { reportsApi } from '../services/api';
import ReactMarkdown from 'react-markdown';

const ACTION_TYPES = [
  { value: 'generate_report', label: '📊 Full Analysis Report', icon: '📊' },
  { value: 'summarize', label: '📝 Summary', icon: '📝' },
  { value: 'compliance_check', label: '✅ Compliance Check', icon: '✅' },
];

function ReportViewer({ documents, selectedReport: externalReport, onReportCleared }) {
  const [report, setReport] = useState(externalReport);
  const [actionType, setActionType] = useState('generate_report');
  const [selectedDocIds, setSelectedDocIds] = useState([]);
  const [query, setQuery] = useState('');
  const [complianceAreas, setComplianceAreas] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  React.useEffect(() => {
    if (externalReport) setReport(externalReport);
  }, [externalReport]);

  const handleGenerate = async () => {
    const docIds = selectedDocIds.length > 0 ? selectedDocIds : documents.map(d => d.document_id);
    if (docIds.length === 0) {
      setError('Please select at least one document');
      return;
    }

    setLoading(true);
    setError(null);
    setReport(null);

    try {
      let result;
      if (actionType === 'compliance_check') {
        const areas = complianceAreas.split(',').map(a => a.trim()).filter(Boolean);
        result = await reportsApi.compliance(docIds, null, areas.length > 0 ? areas : null);
      } else if (actionType === 'summarize') {
        result = await reportsApi.summarize(docIds, query || null);
      } else {
        result = await reportsApi.generate(docIds, actionType, query || null);
      }
      setReport(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const severityColor = (severity) => {
    const colors = { HIGH: 'var(--accent-danger)', MEDIUM: 'var(--accent-warning)', LOW: 'var(--accent-success)' };
    return colors[severity] || 'var(--text-muted)';
  };

  return (
    <div>
      <h2 style={{ marginBottom: 20, fontSize: 22, fontWeight: 700 }}>📊 Reports & Analysis</h2>

      {error && <div className="alert alert-error">❌ {error}</div>}

      {/* Report Configuration */}
      <div className="card">
        <div className="card-title">⚙️ Generate Report</div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          {/* Action Type */}
          <div>
            <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>
              Report Type
            </label>
            <select
              className="input"
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
            >
              {ACTION_TYPES.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          {/* Document Selection */}
          <div>
            <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>
              Documents (leave empty for all)
            </label>
            <select
              className="input"
              multiple
              size={Math.min(documents.length + 1, 4)}
              value={selectedDocIds}
              onChange={(e) => setSelectedDocIds(Array.from(e.target.selectedOptions, o => o.value))}
            >
              {documents.map(doc => (
                <option key={doc.document_id} value={doc.document_id}>
                  {doc.filename && doc.filename.length > 35 ? doc.filename.substring(0, 35) + '...' : doc.filename}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>
            {actionType === 'compliance_check' ? 'Compliance Areas (comma-separated)' : 'Focus/Query (optional)'}
          </label>
          <input
            className="input"
            placeholder={actionType === 'compliance_check'
              ? 'e.g., GDPR, SOX, HIPAA, data privacy'
              : 'e.g., Focus on risk assessment and recommendations'}
            value={actionType === 'compliance_check' ? complianceAreas : query}
            onChange={(e) => actionType === 'compliance_check' ? setComplianceAreas(e.target.value) : setQuery(e.target.value)}
          />
        </div>

        <button
          className="btn btn-primary"
          onClick={handleGenerate}
          disabled={loading || documents.length === 0}
        >
          {loading ? <span className="loading-spinner" /> : '🚀'}
          {loading ? 'Generating...' : 'Generate Report'}
        </button>

        {documents.length === 0 && (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>
            Upload documents first to generate reports.
          </p>
        )}
      </div>

      {/* Report Display */}
      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <div className="loading-spinner" style={{ width: 40, height: 40, margin: '0 auto 16px' }} />
          <div style={{ color: 'var(--text-muted)' }}>AI agents are analyzing your documents...</div>
        </div>
      )}

      {report && !loading && (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div>
              <div className="card-title" style={{ marginBottom: 4 }}>{report.title}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                {report.action_type?.replace(/_/g, ' ').toUpperCase()} ·
                Generated in {Math.round(report.processing_time_ms || 0)}ms ·
                {report.document_ids?.length} document(s)
              </div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => { setReport(null); onReportCleared?.(); }}>
              ✕ Close
            </button>
          </div>

          {/* Summary */}
          {report.summary && (
            <div style={{
              background: 'rgba(79,142,247,0.06)',
              border: '1px solid rgba(79,142,247,0.2)',
              borderRadius: 8, padding: 16, marginBottom: 16, fontSize: 13,
            }}>
              <strong style={{ color: 'var(--accent-primary)' }}>Summary:</strong>
              <div style={{ marginTop: 6, lineHeight: 1.7 }}>{report.summary}</div>
            </div>
          )}

          {/* Compliance Issues */}
          {report.compliance_issues && report.compliance_issues.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10, color: 'var(--accent-warning)' }}>
                ⚠️ Compliance Issues ({report.compliance_issues.length})
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {report.compliance_issues.map((issue, i) => (
                  <div key={i} style={{
                    background: 'rgba(255,167,38,0.05)',
                    border: `1px solid ${severityColor(issue.severity)}40`,
                    borderLeft: `3px solid ${severityColor(issue.severity)}`,
                    borderRadius: 6, padding: '10px 14px',
                  }}>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4 }}>
                      <span className="badge" style={{ background: `${severityColor(issue.severity)}20`, color: severityColor(issue.severity) }}>
                        {issue.severity}
                      </span>
                      <span style={{ fontSize: 12, fontWeight: 500 }}>{issue.area}</span>
                    </div>
                    <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>{issue.description}</div>
                    {issue.recommendation && (
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', fontStyle: 'italic' }}>
                        💡 {issue.recommendation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Key Findings */}
          {report.key_findings && report.key_findings.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>🔑 Key Findings</h3>
              <ul style={{ paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6 }}>
                {report.key_findings.map((finding, i) => (
                  <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{finding}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {report.recommendations && report.recommendations.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10, color: 'var(--accent-success)' }}>
                ✅ Recommendations
              </h3>
              <ul style={{ paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6 }}>
                {report.recommendations.map((rec, i) => (
                  <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Full Content */}
          <details>
            <summary style={{ fontSize: 13, color: 'var(--text-muted)', cursor: 'pointer', marginBottom: 12 }}>
              📄 View Full Report Content
            </summary>
            <div style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: 8, padding: 16,
              fontSize: 13, lineHeight: 1.8,
              maxHeight: 500, overflowY: 'auto',
            }}>
              <ReactMarkdown>{report.content}</ReactMarkdown>
            </div>
          </details>
        </div>
      )}
    </div>
  );
}

export default ReportViewer;
