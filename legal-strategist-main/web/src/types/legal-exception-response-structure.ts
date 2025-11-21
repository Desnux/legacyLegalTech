export interface LegalExceptionResponseStructure {
  summary: string | null;
  court: string | null;
  opening: string | null;
  exception_responses: string[] | null;
  main_request: string | null;
  additional_requests: string | null;
}