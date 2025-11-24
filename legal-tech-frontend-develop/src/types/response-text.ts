export interface ResponseTextInputInformation {
  files: ResponseFile[];
}

export interface ResponseFile {
  id: string;
  file: File;
}

export const EVENT_TYPE_OPTIONS = [
{ value: "exceptions", label: "Excepciones" },
{ value: "dispatch_resolution", label: "Resolución de Despacho" }
];

export interface ResponseTextStructure {
  header?: string | null;
  summary: string;
  court: string;
  opening?: string | null;
  compromise_terms?: string | null;
  exception_responses?: string[];
  main_request: string;
  additional_requests?: string | null;
  content?: string | null;
}

