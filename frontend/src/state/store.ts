import { create } from 'zustand';
import { Contract, Clause, AnalysisSession, ChatMessage } from '../types/contract';

interface AppState {
  // Contracts
  contracts: Contract[];
  activeContractId: string | null;
  activeClauseId: string | null;

  // Session
  session: AnalysisSession | null;

  // UI
  sidebarOpen: boolean;
  compareMode: boolean;
  compareVersionIds: [string | null, string | null];
  activeTab: 'clauses' | 'chat' | 'versions' | 'compare';

  // Actions
  setContracts: (contracts: Contract[]) => void;
  addContract: (contract: Contract) => void;
  updateContract: (id: string, updates: Partial<Contract>) => void;
  setActiveContract: (id: string | null) => void;
  setActiveClause: (id: string | null) => void;
  setSidebarOpen: (open: boolean) => void;
  setCompareMode: (mode: boolean) => void;
  setCompareVersionIds: (ids: [string | null, string | null]) => void;
  setActiveTab: (tab: AppState['activeTab']) => void;
  addMessage: (message: ChatMessage) => void;
  initSession: (contractId: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  contracts: [],
  activeContractId: null,
  activeClauseId: null,
  session: null,
  sidebarOpen: true,
  compareMode: false,
  compareVersionIds: [null, null],
  activeTab: 'clauses',

  setContracts: (contracts) => set({ contracts }),
  addContract: (contract) =>
    set((s) => ({ contracts: [...s.contracts, contract] })),
  updateContract: (id, updates) =>
    set((s) => ({
      contracts: s.contracts.map((c) => (c.id === id ? { ...c, ...updates } : c)),
    })),
  setActiveContract: (id) => set({ activeContractId: id, activeClauseId: null }),
  setActiveClause: (id) => set({ activeClauseId: id }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setCompareMode: (compareMode) => set({ compareMode }),
  setCompareVersionIds: (ids) => set({ compareVersionIds: ids }),
  setActiveTab: (activeTab) => set({ activeTab }),
  addMessage: (message) =>
    set((s) => ({
      session: s.session
        ? { ...s.session, messages: [...s.session.messages, message] }
        : null,
    })),
  initSession: (contractId) =>
    set({
      session: {
        id: crypto.randomUUID(),
        contractId,
        messages: [],
        createdAt: new Date().toISOString(),
      },
    }),
}));