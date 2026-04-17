import React, { useEffect, useState } from 'react';
import { RiskLevel, RiskBreakdown } from '../types/contract';

interface RiskMeterProps {
  score: number;
  level: RiskLevel;
  breakdown: RiskBreakdown;
  summary: string;
}

const levelLabel: Record<RiskLevel, string> = {
  critical: 'CRITICAL RISK',
  high: 'HIGH RISK',
  medium: 'MEDIUM RISK',
  low: 'LOW RISK',
  safe: 'SAFE',
};

const levelColor: Record<RiskLevel, string> = {
  critical: '#ff2d55',
  high: '#ff6b35',
  medium: '#ffd60a',
  low: '#34c759',
  safe: '#30d158',
};

export const RiskMeter: React.FC<RiskMeterProps> = ({ score, level, breakdown, summary }) => {
  const [animScore, setAnimScore] = useState(0);
  const color = levelColor[level];

  useEffect(() => {
    let start = 0;
    const step = score / 40;
    const interval = setInterval(() => {
      start += step;
      if (start >= score) {
        setAnimScore(score);
        clearInterval(interval);
      } else {
        setAnimScore(Math.round(start));
      }
    }, 16);
    return () => clearInterval(interval);
  }, [score]);

  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (animScore / 100) * circumference;
  const total = Object.values(breakdown).reduce((a, b) => a + b, 0);

  return (
    <div className="risk-meter-card">
      <div className="risk-meter-header">
        <h3>Overall Risk Assessment</h3>
      </div>

      <div className="risk-meter-body">
        {/* Gauge */}
        <div className="gauge-wrap">
          <svg viewBox="0 0 128 128" className="gauge-svg">
            <circle cx="64" cy="64" r="54" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
            <circle
              cx="64" cy="64" r="54"
              fill="none"
              stroke={color}
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              transform="rotate(-90 64 64)"
              style={{ transition: 'stroke-dashoffset 0.05s linear, stroke 0.4s' }}
            />
          </svg>
          <div className="gauge-center">
            <span className="gauge-score" style={{ color }}>{animScore}</span>
            <span className="gauge-label" style={{ color }}>{levelLabel[level]}</span>
          </div>
        </div>

        {/* Breakdown bars */}
        <div className="breakdown-wrap">
          {(Object.entries(breakdown) as [RiskLevel, number][]).map(([lvl, count]) => (
            <div key={lvl} className="breakdown-row">
              <span className="breakdown-name" style={{ color: levelColor[lvl] }}>
                {lvl.toUpperCase()}
              </span>
              <div className="breakdown-bar-bg">
                <div
                  className="breakdown-bar-fill"
                  style={{
                    width: total ? `${(count / total) * 100}%` : '0%',
                    background: levelColor[lvl],
                  }}
                />
              </div>
              <span className="breakdown-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="risk-summary">
        <p className="risk-summary-label">AI ANALYSIS</p>
        <p className="risk-summary-text">{summary}</p>
      </div>
    </div>
  );
};