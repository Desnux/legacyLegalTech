export type CaseProbableStats = {
  days_to_resolve: number | null;
  compromise_chance: number | null;
  compromise_amount_percentage: number | null;
  withdrawal_chance: number | null;
}

export type Case = {
  id: string;
  case_recepthor_id: string | null;
  title: string;
  city: string;
  legal_subject: 'promissory_note_collection' | 'bill_collection' | 'general_collection';
  winner: 'plaintiffs' | 'defendants' | 'court' | 'external_party' | null;
  status: 'draft' | 'active' | 'archived' | 'finished';
  created_at: string;
  stats: CaseProbableStats | null;
  simulated: boolean;
  litigants: LitigantInformation[];
  latest_step: string;
  amount: number;
  events: CaseEvents[] | null;
  details: CaseDetailInfo | null;
};

export type CaseListType = Omit<Case,'details' | 'stats' | 'case_recepthor_id' | 'city'> & {
  amount_currency: string;
  tribunal: string;
  court: string;
  year: number;
  rol: number;
};

export type CaseDetailInfo = {
  year: number;
  role: number;
  tribunal_id: string;
  tribunal: Tribunal;
  court_id: string;
  court: Court;
}

export type CreateCaseDetail = {
  year: number;
  role: number;
  tribunal_id: string;
  court_id: string;
}

export type Tribunal = {
  id: string;
  recepthor_id: string;
  name: string;
  code: number;
  court_id: string;
}

export type Court = {
  id: string;
  recepthor_id: string;
  name: string;
  code: number;
}

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
  legal_subject: 'promissory_note_collection' | 'bill_collection' | 'general_collection';
  winner: string | null;
  status: string;
  created_at: string | null;
  latest_step: string;
  court: string;
  link?: boolean;
  events: CaseEvents[] | null;
  simulated?: boolean;
};

export interface CaseEvents {
  type: string; 
  date: string | null;
}

export interface LitigantInformation {
    id: string;
    name: string;
    rut: string;
    address: string | null;
    role:  'plaintiff' | 'sponsoring_attorney' | 'plaintiff_legal_representative' | 'defendant' | 'legal_representative' | 'guarantee';
    simulated: boolean;
    is_co_debtor: boolean;
}

export interface CaseStatsParams {
  skip?: number;
  limit?: number;
  bank?: string;
  status?: string[];
  order_by?: string;
  order_direction?: string;
};

export interface CaseListResponse {
  cases: CaseListType[];
  case_count: number;
}

export interface CaseStatsResponse {
  cases: Case[];
  case_count: number;
}
