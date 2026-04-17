import { Contract, Clause, RiskLevel } from '../types/contract';

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

const SAMPLE_CLAUSES: Clause[] = [
  {
    id: 'c1',
    title: 'Limitation of Liability',
    text: 'In no event shall either party be liable for any indirect, incidental, special, exemplary, or consequential damages, however caused, even if such party has been advised of the possibility of such damages.',
    riskLevel: 'high',
    riskScore: 78,
    explanation: 'This clause broadly excludes consequential damages, which could severely limit your ability to recover losses if the counterparty breaches the agreement.',
    suggestions: [
      'Add a carve-out for gross negligence and willful misconduct',
      'Cap the limitation at a reasonable multiple of fees paid',
      'Explicitly exclude IP indemnification from liability cap',
    ],
  },
  {
    id: 'c2',
    title: 'Indemnification',
    text: 'You shall indemnify, defend, and hold harmless the Company and its affiliates from any claims arising from your use of the service, your content, or your violation of these terms.',
    riskLevel: 'critical',
    riskScore: 91,
    explanation: 'One-sided indemnification that places nearly all risk on you. No mutual indemnity and no cap on the indemnification obligation.',
    suggestions: [
      'Require mutual indemnification obligations',
      'Add a carve-out for claims arising from the Company\'s own negligence',
      'Cap indemnification liability at the contract value',
    ],
  },
  {
    id: 'c3',
    title: 'Intellectual Property Assignment',
    text: 'All work product, inventions, and deliverables created by Consultant in connection with the Services shall be the exclusive property of the Company.',
    riskLevel: 'critical',
    riskScore: 88,
    explanation: 'Broad IP assignment that may capture pre-existing IP and background technology. No exclusion for independent developments.',
    suggestions: [
      'Add a schedule of pre-existing IP that is excluded',
      'Limit assignment to work created specifically under this contract',
      'Negotiate a license-back for your general methodologies',
    ],
  },
  {
    id: 'c4',
    title: 'Termination for Convenience',
    text: 'Either party may terminate this Agreement at any time with 30 days written notice. Upon termination, Company\'s sole obligation is to pay for services rendered through the termination date.',
    riskLevel: 'medium',
    riskScore: 52,
    explanation: 'Termination notice period is short for a complex engagement. No kill fee or transition assistance fee is included.',
    suggestions: [
      'Negotiate a 60-90 day notice period',
      'Add a kill fee of 20-25% of remaining contract value',
      'Include a transition assistance clause',
    ],
  },
  {
    id: 'c5',
    title: 'Governing Law & Jurisdiction',
    text: 'This Agreement shall be governed by the laws of the State of Delaware, and the parties consent to exclusive jurisdiction in the courts of New Castle County, Delaware.',
    riskLevel: 'low',
    riskScore: 28,
    explanation: 'Delaware jurisdiction is standard and reasonably neutral for commercial contracts.',
    suggestions: [
      'Consider adding an arbitration clause for faster dispute resolution',
    ],
  },
  {
    id: 'c6',
    title: 'Confidentiality',
    text: 'Each party agrees to maintain the confidentiality of the other party\'s Confidential Information for a period of 3 years following termination of this Agreement.',
    riskLevel: 'low',
    riskScore: 22,
    explanation: 'Standard mutual NDA with reasonable duration. Adequately protects both parties.',
    suggestions: [
      'Extend protection for trade secrets to be indefinite',
    ],
  },
  {
    id: 'c7',
    title: 'Non-Compete',
    text: 'For a period of 24 months following termination, you agree not to engage in any business activity that competes with the Company\'s business within the United States.',
    riskLevel: 'high',
    riskScore: 82,
    explanation: 'Broad geographic scope (entire US) and lengthy duration (24 months) may be unenforceable in many jurisdictions but still poses legal risk.',
    suggestions: [
      'Limit geographic scope to specific markets where Company operates',
      'Reduce duration to 12 months',
      'Add specific definition of "competing business"',
      'Require compensation during non-compete period',
    ],
  },
  {
    id: 'c8',
    title: 'Payment Terms',
    text: 'Invoices are due within 60 days of receipt. Company reserves the right to withhold payment for disputed deliverables without interest.',
    riskLevel: 'medium',
    riskScore: 48,
    explanation: '60-day net terms are longer than industry standard. No interest on late payments weakens your position.',
    suggestions: [
      'Negotiate Net-30 payment terms',
      'Add 1.5% monthly interest on overdue amounts',
      'Define clear dispute resolution process with timeline',
    ],
  },
];

export const mockApi = {
  async uploadContract(file: File): Promise<Contract> {
    await delay(2000);
    const id = crypto.randomUUID();
    return {
      id,
      filename: file.name,
      uploadedAt: new Date().toISOString(),
      status: 'analyzed',
      overallRiskScore: 71,
      overallRiskLevel: 'high',
      clauses: SAMPLE_CLAUSES,
      summary:
        'This service agreement contains several high-risk provisions that disproportionately favor the Company. Key concerns include a one-sided indemnification clause, broad IP assignment without pre-existing IP carve-outs, and an overly broad non-compete. Immediate legal review is recommended before signing.',
      parties: ['Acme Corp (Company)', 'John Doe (Consultant)'],
      effectiveDate: '2025-01-01',
      versions: [
        {
          id: `v1-${id}`,
          contractId: id,
          version: 1,
          uploadedAt: new Date().toISOString(),
          filename: file.name,
          overallRisk: 71,
          clauseCount: SAMPLE_CLAUSES.length,
        },
      ],
    };
  },

  async chat(contractId: string, message: string, history: {role: string, content: string}[]): Promise<string> {
    await delay(1200);
    const responses: Record<string, string> = {
      default: `Based on my analysis of this contract, I can help you understand the specific risks. The clause you're asking about presents several concerns from a legal standpoint. I recommend consulting with a qualified attorney before signing.`,
      risk: `The overall risk score is 71/100 (High). The two most critical issues are the one-sided indemnification (91/100) and the broad IP assignment clause (88/100). These should be your priority in negotiations.`,
      negotiate: `For negotiation strategy, I suggest: 1) Prioritize the indemnification clause — push for mutual indemnity. 2) Carve out pre-existing IP explicitly. 3) Request a liability cap equal to fees paid in the 12 months prior to the claim.`,
    };
    const lower = message.toLowerCase();
    if (lower.includes('risk') || lower.includes('score')) return responses.risk;
    if (lower.includes('negotiate') || lower.includes('strategy')) return responses.negotiate;
    return responses.default;
  },
};