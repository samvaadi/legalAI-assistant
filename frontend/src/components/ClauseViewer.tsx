import React, { useState } from 'react';
import { Clause, RiskLevel } from '../types/contract';
import { useAppStore } from '../state/store';

const levelColor: Record<RiskLevel, string> = {
  critical: '#ff2d55',
  high: '#ff6b35',
  medium: '#ffd60a',
  low: '#34c759',
  safe: '#30d158',
};

const levelBg: Record<RiskLevel, string> = {
  critical: 'rgba(255,45,85,0.08)',
  high: 'rgba(255,107,53,0.08)',
  medium: 'rgba(255,214,10,0.08)',
  low: 'rgba(52,199,89,0.08)',
  safe: 'rgba(48,209,88,0.08)',
};

interface ClauseViewerProps {
  clauses: Clause[];
}

export const ClauseViewer: React.FC<ClauseViewerProps> = ({ clauses }) => {
  const { activeClauseId, setActiveClause } = useAppStore();
  const [filter, setFilter] = useState<RiskLevel | 'all'>('all');
  const [search, setSearch] = useState('');

  const filtered = clauses
    .filter((c) => filter === 'all' || c.riskLevel === filter)
    .filter((c) =>
      !search ||
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.text.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => b.riskScore - a.riskScore);

  return (
    <div className="clause-viewer">
      {/* Filters */}
      <div className="clause-controls">
        <input
          className="clause-search"
          placeholder="Search clauses…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="clause-filters">
          {(['all', 'critical', 'high', 'medium', 'low', 'safe'] as const).map((lvl) => (
            <button
              key={lvl}
              className={`filter-pill ${filter === lvl ? 'active' : ''}`}
              style={filter === lvl && lvl !== 'all' ? {
                background: levelColor[lvl as RiskLevel],
                color: '#000',
                borderColor: levelColor[lvl as RiskLevel],
              } : {}}
              onClick={() => setFilter(lvl)}
            >
              {lvl.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Clause List */}
      <div className="clause-list">
        {filtered.length === 0 && (
          <div className="clause-empty">No clauses match your filter.</div>
        )}
        {filtered.map((clause) => (
          <ClauseCard
            key={clause.id}
            clause={clause}
            active={clause.id === activeClauseId}
            onClick={() => setActiveClause(clause.id === activeClauseId ? null : clause.id)}
          />
        ))}
      </div>
    </div>
  );
};

const ClauseCard: React.FC<{
  clause: Clause;
  active: boolean;
  onClick: () => void;
}> = ({ clause, active, onClick }) => {
  const color = levelColor[clause.riskLevel];
  const bg = levelBg[clause.riskLevel];

  return (
    <div
      className={`clause-card ${active ? 'expanded' : ''}`}
      style={{ borderLeftColor: color }}
      onClick={onClick}
    >
      <div className="clause-card-header">
        <div className="clause-card-title-row">
          <span className="clause-title">{clause.title}</span>
          <div className="clause-badges">
            <span className="clause-risk-badge" style={{ background: bg, color, border: `1px solid ${color}` }}>
              {clause.riskLevel.toUpperCase()}
            </span>
            <span className="clause-score" style={{ color }}>
              {clause.riskScore}
            </span>
          </div>
        </div>

        {/* Score bar */}
        <div className="clause-score-bar-bg">
          <div
            className="clause-score-bar-fill"
            style={{ width: `${clause.riskScore}%`, background: color }}
          />
        </div>
      </div>

      {active && (
        <div className="clause-card-body">
          <div className="clause-text-block">
            <p className="clause-section-label">CONTRACT LANGUAGE</p>
            <p className="clause-text">"{clause.text}"</p>
          </div>

          <div className="clause-analysis-block">
            <p className="clause-section-label">AI ANALYSIS</p>
            <p className="clause-explanation">{clause.explanation}</p>
          </div>

          {clause.suggestions.length > 0 && (
            <div className="clause-suggestions-block">
              <p className="clause-section-label">RECOMMENDED CHANGES</p>
              <ul className="clause-suggestions-list">
                {clause.suggestions.map((s, i) => (
                  <li key={i} className="clause-suggestion-item">
                    <span className="suggestion-arrow">→</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};