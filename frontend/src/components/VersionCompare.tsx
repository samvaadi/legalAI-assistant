import React from 'react';
import { ContractVersion, DiffChange } from '../types/contract';

interface VersionCompareProps {
  versions: ContractVersion[];
}

const mockChanges: DiffChange[] = [
  {
    type: 'modified',
    clauseId: 'c1',
    clauseTitle: 'Limitation of Liability',
    oldText: 'Liability is limited to direct damages only.',
    newText: 'In no event shall either party be liable for any indirect, incidental, special, exemplary, or consequential damages.',
    riskDelta: +32,
  },
  {
    type: 'added',
    clauseId: 'c7',
    clauseTitle: 'Non-Compete',
    newText: 'For a period of 24 months following termination, you agree not to engage in any competing business within the United States.',
    riskDelta: +82,
  },
  {
    type: 'removed',
    clauseId: 'c9',
    clauseTitle: 'Arbitration Clause',
    oldText: 'All disputes shall be resolved through binding arbitration under AAA rules.',
    riskDelta: -15,
  },
];

export const VersionCompare: React.FC<VersionCompareProps> = ({ versions }) => {
  if (versions.length < 2) {
    return (
      <div className="version-empty">
        <div className="version-empty-icon">🔄</div>
        <h3>Version Comparison</h3>
        <p>Upload a second version of this contract to compare changes and track risk evolution.</p>
      </div>
    );
  }

  const v1 = versions[0];
  const v2 = versions[versions.length - 1];
  const riskDelta = v2.overallRisk - v1.overallRisk;

  return (
    <div className="version-compare">
      {/* Header */}
      <div className="version-header-row">
        <VersionBadge version={v1} label="Version 1" />
        <div className="version-delta">
          <span className="delta-arrow">→</span>
          <span
            className="delta-value"
            style={{ color: riskDelta > 0 ? '#ff2d55' : '#34c759' }}
          >
            {riskDelta > 0 ? '+' : ''}{riskDelta} risk
          </span>
        </div>
        <VersionBadge version={v2} label={`Version ${versions.length}`} />
      </div>

      {/* Changes */}
      <div className="changes-list">
        <p className="changes-label">DETECTED CHANGES ({mockChanges.length})</p>
        {mockChanges.map((change) => (
          <ChangeItem key={change.clauseId} change={change} />
        ))}
      </div>
    </div>
  );
};

const VersionBadge: React.FC<{ version: ContractVersion; label: string }> = ({ version, label }) => (
  <div className="version-badge">
    <p className="version-badge-label">{label}</p>
    <p className="version-badge-file">{version.filename}</p>
    <p className="version-badge-date">
      {new Date(version.uploadedAt).toLocaleDateString()}
    </p>
    <div className="version-badge-risk">
      Risk Score: <strong>{version.overallRisk}</strong>
    </div>
  </div>
);

const typeConfig = {
  added: { label: 'ADDED', color: '#34c759', icon: '+' },
  removed: { label: 'REMOVED', color: '#ff2d55', icon: '−' },
  modified: { label: 'MODIFIED', color: '#ffd60a', icon: '~' },
};

const ChangeItem: React.FC<{ change: DiffChange }> = ({ change }) => {
  const cfg = typeConfig[change.type];

  return (
    <div className="change-item" style={{ borderLeftColor: cfg.color }}>
      <div className="change-item-header">
        <div className="change-type-badge" style={{ background: `${cfg.color}22`, color: cfg.color }}>
          <span>{cfg.icon}</span> {cfg.label}
        </div>
        <span className="change-clause-title">{change.clauseTitle}</span>
        {change.riskDelta !== undefined && (
          <span
            className="change-risk-delta"
            style={{ color: (change.riskDelta ?? 0) > 0 ? '#ff2d55' : '#34c759' }}
          >
            {(change.riskDelta ?? 0) > 0 ? '▲' : '▼'} {Math.abs(change.riskDelta ?? 0)} risk
          </span>
        )}
      </div>

      <div className="change-texts">
        {change.oldText && (
          <div className="change-old">
            <span className="change-text-label">BEFORE</span>
            <p>{change.oldText}</p>
          </div>
        )}
        {change.newText && (
          <div className="change-new">
            <span className="change-text-label">AFTER</span>
            <p>{change.newText}</p>
          </div>
        )}
      </div>
    </div>
  );
};