const FILE_TYPES = [
  "promissory_note",
  "bill",
  "bond",
  "response",
] as const;

export type FileType = typeof FILE_TYPES[number];

export interface FileWithContext {
  id: string;
  file: File;
  context: string;
  promissory_number: number;
  fileType: FileType;
}
