const LEGAL_SUBJECTS = ["promisory_note_collection", "bill_collection", "general_collection"] as const;

export type LegalSubject = typeof LEGAL_SUBJECTS[number];
