export type Event = {
  id: string;
  title: string;
  content: Record<string, any> | null;
  source: 'plaintiffs' | 'defendants' | 'court' | 'external_party' | null;
  target: 'plaintiffs' | 'defendants' | 'court' | 'external_party' | null;
  type: string;
  created_at: string;
  previous_event_id: string | null;
  next_event_id: string | null;
  document_count: number;
  simulated: boolean;
  procedure_date: string | null;
};
