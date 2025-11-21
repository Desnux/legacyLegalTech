export interface MissingField {
  label: string;
  type: "string" | "number" | "select" | "list";
  name: string;
  initial_value?: string | MissingField[];
  corrected_value?: string | MissingField[];
  options?: { label: string; value: string }[];
}
