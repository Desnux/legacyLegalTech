export interface Milestone {
  id?: string;
  folio?: string;
  document?: string[];
  annex?: string[];
  stage: string;
  procedure: string;
  procedureDescription: string;
  procedureDate: string;
  page: number;
  actionToFollow?: string;
  responsiblePerson?: string;
  deadline?: string;
  createdAt: string;
  updatedAt: string;
}
