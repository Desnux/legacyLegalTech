import { Analysis } from "@/types/analysis";
import { MissingField } from "@/types/field";
import { Attorney, Defendant, Plaintiff } from "@/types/litigant";
import { FileType } from "./file";


export interface MissingPaymentArgument {
  argument: string,
  document_type: FileType,
}

export interface DemandTextAnalysis {
  header: Analysis | null;
  summary: Analysis | null;
  court: Analysis | null;
  opening: Analysis | null;
  missing_payment_arguments: Analysis[] | null;
  main_request: Analysis | null;
  additional_requests: Analysis | null;
  overall: Analysis | null;
}

export interface DemandTextCorrectionForm {
  defendants: MissingField[][];
  plaintiffs: MissingField[][];
  bills: MissingField[][];
  promissory_notes: MissingField[][];
  sponsoring_attorneys: MissingField[][];
}

export interface DemandTextStructure {
  header: string | null;
  summary: string | null;
  court: string | null;
  opening: string | null;
  missing_payment_arguments: MissingPaymentArgument[] | null;
  main_request: string | null;
  additional_requests: string | null;
  sponsoring_attorneys?: Attorney[] | null;
  plaintiffs?: Plaintiff[] | null;
  defendants?: Defendant[] | null;
  legal_subject?: string | null;
}
