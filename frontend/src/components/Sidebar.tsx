import React from 'react';
import { useAppStore } from '../state/store';
import { Contract, RiskLevel } from '../types/contract';

const riskColors: Record<RiskLevel, string> = {
  critical: '#ff2d55',
  high: '#ff6b35',
  medium: '#ffd60a',
  low: '#34c759',
  safe: '#30d158',
};

const riskBg: Record<RiskLevel, string> = {
  critical: 'rgba(255,45,85,0.12)',
  high: 'rgba(255,107,53,0.12)',
  medium: 'rgba(255,214,10,0.12)',
  low: 'rgba(52,199,89,0.12)',
  safe: 'rgba(48,209,88,0.12)',
};

interface SidebarProps {
  onUploadClick: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onUploadClick }) => {
  const { contracts, activeContractId, setActiveContract, sidebarOpen, setSidebarOpen } = useAppStore();

  return (
    <>
      {/* Backdrop for mobile */}
      {sidebarOpen && (
        <div
          className="sidebar-backdrop"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="logo-mark">⚖</div>
          <div className="logo-text">
            <span className="logo-primary">Lex</span>
            <span className="logo-accent">AI</span>
          </div>
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(false)}>
            ←
          </button>
        </div>

        {/* Upload Button */}
        <button className="upload-btn" onClick={onUploadClick}>
          <span className="upload-icon">+</span>
          <span>Analyze Contract</span>
        </button>

        {/* Contract List */}
        <div className="sidebar-section">
          <p className="sidebar-label">RECENT CONTRACTS</p>
          {contracts.length === 0 ? (
            <p className="sidebar-empty">No contracts yet</p>
          ) : (
            <ul className="contract-list">
              {contracts.map((c) => (
                <ContractItem
                  key={c.id}
                  contract={c}
                  active={c.id === activeContractId}
                  onClick={() => setActiveContract(c.id)}
                />
              ))}
            </ul>
          )}
        </div>

        {/* Footer */}
        <div className="sidebar-footer">
          <div className="sidebar-footer-row">
            <span className="footer-dot" />
            <span>AI Legal Analysis</span>
          </div>
          <p className="footer-disclaimer">Not a substitute for legal counsel</p>
        </div>
      </aside>
    </>
  );
};

const ContractItem: React.FC<{
  contract: Contract;
  active: boolean;
  onClick: () => void;
}> = ({ contract, active, onClick }) => {
  const color = riskColors[contract.overallRiskLevel];
  const bg = riskBg[contract.overallRiskLevel];
  const date = new Date(contract.uploadedAt).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric',
  });

  return (
    <li
      className={`contract-item ${active ? 'active' : ''}`}
      onClick={onClick}
    >
      <div className="contract-item-icon" style={{ background: bg, borderColor: color }}>
        📄
      </div>
      <div className="contract-item-info">
        <p className="contract-item-name">{contract.filename.replace(/\.[^.]+$/, '')}</p>
        <p className="contract-item-meta">{date} · {contract.clauses.length} clauses</p>
      </div>
      <div
        className="contract-item-risk"
        style={{ background: bg, color }}
      >
        {contract.overallRiskScore}
      </div>
    </li>
  );
};