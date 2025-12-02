import { Analysis } from "@/types/analysis";
import { CurrencyType } from "@/types/currency";
import { FileType } from "@/types/file";
import { LegalSubject } from "@/types/legal-subject";

export interface MissingPaymentArgument {
  argument: string,
  document_type: FileType,
}

export interface DemandTextAnalysis {
  header: Analysis | null,
  summary: Analysis | null,
  court: Analysis | null,
  opening: Analysis | null,
  missing_payment_arguments: Analysis[] | null,
  main_request: Analysis | null,
  additional_requests: Analysis | null,
  overall: Analysis | null,
}

export interface DemandTextStructure {
  header: string | null,
  summary: string | null,
  court: string | null,
  opening: string | null,
  missing_payment_arguments: MissingPaymentArgument[] | null,
  main_request: string | null,
  additional_requests: string | null,
}

export enum EntityType {
  NATURAL = 'natural',
  LEGAL = 'legal'
}

export enum ParticipantRole {
  PLAINTIFF = 'plaintiff',
  SPONSORING_ATTORNEY = 'sponsoring_attorney',
  PLAINTIFF_LEGAL_REPRESENTATIVE = 'plaintiff_legal_representative',
  DEFENDANT = 'defendant',
  LEGAL_REPRESENTATIVE = 'legal_representative',
  GUARANTEE = 'guarantee'
}

export interface Participant {
  name: string;
  dni: string;
  address: string;
  legal_representatives?: Participant[];
  entity_type?: EntityType;
  role: ParticipantRole;
  id: string;
}

export interface DemandTextInputInformation {
  amount?: number,
  amount_currency?: CurrencyType,
  city?: string,
  creditors?: Record<string, any>[],
  defendants?: Record<string, any>[],
  documents?: (Record<string, any> | Record<string, any>)[],
  document_types?: Record<string, any>[],
  main_request?: string,
  plaintiff?: Record<string, any>,
  legal_subject?: LegalSubject,
  legal_representatives?: Record<string, any>[],
  reasons_per_document?: Record<string, any>[],
  secondary_requests?: Record<string, any>[],
  sponsoring_attorneys?: Record<string, any>[],
}

export interface DemandExceptionStructure {
  header: string | null;
  court: string | null | undefined;
  opening: string | null;
  summary: string | null;
  exceptions: string | null;
  main_request: string | null;
  additional_requests: string | null;
}

export interface DispatchResolutionStructure {
  header: string | null;
  date_line: string | null;
  resolution: string | null;
  footer: string | null;
}
