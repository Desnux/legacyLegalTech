const ANALYSIS_STATUSES = [
  "good",
  "warning",
  "error",
] as const;

const ANALYSIS_TAGS = [
  "contradiction",
  "bad_spelling",
  "bad_math",
  "missing_info",
  "too_repetitive",
  "informal_language",
  "false_information",
  "possible_ocr_error",
] as const;

export type AnalysisStatus = typeof ANALYSIS_STATUSES[number];

export type AnalysisTag = typeof ANALYSIS_TAGS[number];

export interface Analysis {
  feedback: string | null;
  improvement_suggestions: string | null;
  tags: (string | AnalysisTag)[] | null;
  status: AnalysisStatus | null;
  score: number | null;
}
