export type CaseProbableStats = {
  days_to_resolve: number | null;
  compromise_chance: number | null;
  compromise_amount_percentage: number | null;
  withdrawal_chance: number | null;
}

export type Case = {
  id: string;
  title: string;
  city: string;
  legal_subject: 'promissory_note_collection' | 'bill_collection' | 'general_collection';
  winner: 'plaintiffs' | 'defendants' | 'court' | 'external_party' | null;
  status: 'draft' | 'active' | 'archived' | 'finished';
  created_at: string;
  stats: CaseProbableStats | null;
  simulated: boolean;
};

export type CaseEventSuggestion = {
  id: string, // (formato UUID)
  case_event_id: string, // (formato UUID)
  name: string,
  type: 'demand_text_correction' | 'exceptions_response' | 'response' | 'request' | 'compromise' | 'withdrawal' | 'other',
  content: Record<string, any> | null,
  storage_key: string | null,
  score: number // (valor entre 0.0 y 1.0, inclusive)
};

export interface CaseStats {
  id: string;
  title: string;
  legal_subject: string;
  winner: string | null;
  status: string;
  created_at: string | null;
  latest_step: string;
  court: string;
  link?: boolean;
  events?: { 
    type: string; 
    date: string | null;
  }[];
  simulated?: boolean;
};

export interface CaseStatsParams {
  skip?: number;
  limit?: number;
  bank?: string;
  status?: string[];
  order_by?: string;
  order_direction?: string;
};

export interface CaseStatsResponse {
  cases: CaseStats[];
  case_count: number;
}
