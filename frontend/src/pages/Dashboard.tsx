import React, { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { UploadBox } from '../components/UploadBox';
import { RiskMeter } from '../components/RiskMeter';
import { ClauseViewer } from '../components/ClauseViewer';
import { Suggestions } from '../components/Suggestions';
import { VersionCompare } from '../components/VersionCompare';
import { useAppStore } from '../state/store';
import { mockApi } from '../services/mockApi';
import { Clause, RiskBreakdown } from '../types/contract';

function computeBreakdown(clauses: Clause[]): RiskBreakdown {
  const bd: RiskBreakdown = { critical: 0, high: 0, medium: 0, low: 0, safe: 0 };
  clauses.forEach((c) => bd[c.riskLevel]++);
  return bd;
}

export const Dashboard: React.FC = () => {
  const {
    contracts, activeContractId, sidebarOpen, setSidebarOpen,
    addContract, updateContract, setActiveContract, setActiveTab, activeTab,
  } = useAppStore();

  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);

  const activeContract = contracts.find((c) => c.id === activeContractId) ?? null;

  const handleFile = async (file: File) => {
    setUploading(true);
    try {
      const contract = await mockApi.uploadContract(file);
      addContract(contract);
      setActiveContract(contract.id);
      setShowUpload(false);
      setActiveTab('clauses');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={`dashboard ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      <Sidebar onUploadClick={() => setShowUpload(true)} />

      {/* Main */}
      <main className="main-content">
        {/* Topbar */}
        <header className="topbar">
          {!sidebarOpen && (
            <button className="menu-btn" onClick={() => setSidebarOpen(true)}>☰</button>
          )}
          <div className="topbar-title">
            {activeContract ? activeContract.filename : 'LexAI — Legal Contract Analyzer'}
          </div>
          {activeContract && (
            <div className="topbar-tabs">
              {(['clauses', 'chat', 'versions', 'compare'] as const).map((tab) => (
                <button
                  key={tab}
                  className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab === 'clauses' && '📋 '}
                  {tab === 'chat' && '💬 '}
                  {tab === 'versions' && '🕐 '}
                  {tab === 'compare' && '🔄 '}
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>
          )}
          <button className="upload-top-btn" onClick={() => setShowUpload(true)}>
            + Analyze
          </button>
        </header>

        {/* Body */}
        <div className="content-body">
          {!activeContract ? (
            <EmptyState onUpload={() => setShowUpload(true)} />
          ) : (
            <>
              {activeTab === 'clauses' && (
                <div className="clauses-layout">
                  <div className="risk-column">
                    <RiskMeter
                      score={activeContract.overallRiskScore}
                      level={activeContract.overallRiskLevel}
                      breakdown={computeBreakdown(activeContract.clauses)}
                      summary={activeContract.summary}
                    />
                    <div className="contract-meta-card">
                      <p className="meta-label">CONTRACT DETAILS</p>
                      {activeContract.parties?.map((p, i) => (
                        <div key={i} className="meta-row">
                          <span className="meta-key">Party {i + 1}</span>
                          <span className="meta-val">{p}</span>
                        </div>
                      ))}
                      {activeContract.effectiveDate && (
                        <div className="meta-row">
                          <span className="meta-key">Effective</span>
                          <span className="meta-val">{activeContract.effectiveDate}</span>
                        </div>
                      )}
                      <div className="meta-row">
                        <span className="meta-key">Clauses</span>
                        <span className="meta-val">{activeContract.clauses.length}</span>
                      </div>
                    </div>
                  </div>
                  <div className="clauses-column">
                    <ClauseViewer clauses={activeContract.clauses} />
                  </div>
                </div>
              )}

              {activeTab === 'chat' && (
                <div className="chat-layout">
                  <Suggestions />
                </div>
              )}

              {activeTab === 'versions' && (
                <div className="versions-layout">
                  <div className="versions-timeline">
                    <p className="versions-label">VERSION HISTORY</p>
                    {activeContract.versions.map((v, i) => (
                      <div key={v.id} className="version-timeline-item">
                        <div className="vtl-dot" />
                        <div className="vtl-content">
                          <p className="vtl-title">Version {v.version}</p>
                          <p className="vtl-meta">{new Date(v.uploadedAt).toLocaleString()} · Risk: {v.overallRisk}</p>
                          <p className="vtl-file">{v.filename}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'compare' && (
                <div className="compare-layout">
                  <VersionCompare versions={activeContract.versions} />
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {showUpload && (
        <UploadBox onFile={handleFile} loading={uploading} />
      )}
    </div>
  );
};

const EmptyState: React.FC<{ onUpload: () => void }> = ({ onUpload }) => (
  <div className="empty-state">
    <div className="empty-glyph">⚖</div>
    <h2>Analyze Your Contract</h2>
    <p>Upload a PDF or DOCX to get instant AI-powered risk scoring, clause extraction, and negotiation recommendations.</p>
    <button className="empty-upload-btn" onClick={onUpload}>
      Upload Contract
    </button>
    <div className="empty-features">
      {[
        ['🔍', 'Risk Scoring', 'Every clause scored 0–100'],
        ['📋', 'Clause Extraction', 'Auto-identify key provisions'],
        ['💡', 'Rewrites', 'AI-suggested improvements'],
        ['🔄', 'Version Diff', 'Track changes across drafts'],
      ].map(([icon, title, desc]) => (
        <div key={title} className="empty-feature">
          <span className="ef-icon">{icon}</span>
          <strong>{title}</strong>
          <span>{desc}</span>
        </div>
      ))}
    </div>
  </div>
);