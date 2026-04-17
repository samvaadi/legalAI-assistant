export type RiskLevel = 'critical' | 'high' | 'medium' | 'low' | 'safe';

export interface Clause {
  id: string;
  title: string;
  text: string;
  riskLevel: RiskLevel;
  riskScore: number;
  explanation: string;
  suggestions: string[];
  page?: number;
  highlighted?: boolean;
}

export interface ContractVersion {
  id: string;
  contractId: string;
  version: number;
  uploadedAt: string;
  filename: string;
  overallRisk: number;
  clauseCount: number;
  changes?: DiffChange[];
}

export interface DiffChange {
  type: 'added' | 'removed' | 'modified';
  clauseId: string;
  clauseTitle: string;
  oldText?: string;
  newText?: string;
  riskDelta?: number;
}

export interface Contract {
  id: string;
  filename: string;
  uploadedAt: string;
  status: 'uploading' | 'processing' | 'analyzed' | 'error';
  overallRiskScore: number;
  overallRiskLevel: RiskLevel;
  clauses: Clause[];
  summary: string;
  parties?: string[];
  effectiveDate?: string;
  versions: ContractVersion[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  relatedClauses?: string[];
}

export interface AnalysisSession {
  id: string;
  contractId: string;
  messages: ChatMessage[];
  createdAt: string;
}

export interface RiskBreakdown {
  critical: number;
  high: number;
  medium: number;
  low: number;
  safe: number;
}