export interface WithdrawalStructure {
  header: string | null;
  summary: string | null;
  court: string | null;
  content: string | null;
  main_request: string | null;
}

export function isWithdrawalStructure(content: any): content is WithdrawalStructure {
  return (
    typeof
      content.header === "string" ||
      content.header === null &&
    typeof
      content.summary === "string" ||
      content.summary === null &&
    typeof
      content.court === "string" ||
      content.court === null &&
    typeof
      content.content === "string" ||
      content.content === null &&
    typeof
      content.main_request === "string" ||
      content.main_request === null
  );
}
