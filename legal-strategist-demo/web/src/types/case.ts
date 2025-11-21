export type Case = {
  id: string;
  title: string;
  city: string;
  legal_subject: 'promissory_note_collection' | 'bill_collection' | 'general_collection';
  winner: 'plaintiffs' | 'defendants' | 'court' | 'external_party' | null;
  status: 'draft' | 'active' | 'archived' | 'finished';
  created_at: string;
};

export type CaseEventSuggestion = {
  id: string, // (formato UUID)
  case_event_id: string, // (formato UUID)
  name: string,
  type: 'demand_text_correction' | 'exceptions_response' | 'response' | 'request' | 'compromise' | 'other',
  content: Record<string, any> | null,
  storage_key: string | null,
  score: number // (valor entre 0.0 y 1.0, inclusive)
};