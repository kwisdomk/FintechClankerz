export interface Transaction {
  id: string;
  date: string;
  description: string;
  supplier: string;
  amount: number;
  category: string;
  status: 'normal' | 'flagged' | 'pending';
}

export interface AnomalyFinding {
  id: string;
  transactionId: string;
  type: string;
  severity: 'low' | 'medium' | 'high';
  reviewStatus: 'open' | 'investigating' | 'resolved';
  explanation: string;
}