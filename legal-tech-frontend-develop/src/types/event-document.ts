export type EventDocument = {
  id: string;
  case_event_id: string;
  author_id: string | null;
  name: string;
  type: 'demand_text' | 'exceptions' | 'dispatch_resolution' | 'resolution' | 'exceptions_response' | 'request' | 'exceptions_response' | 'demand_text_correction' | 'response' | 'other';
  content: Record<string, any> | null;
  updated_at: string;
  created_at: string;
  storage_key: string | null;
  simulated: boolean;
};
