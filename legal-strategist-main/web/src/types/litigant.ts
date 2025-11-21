export interface Attorney {
  raw_name: string;
  identifier: string;
}

export interface LegalRepresentative {
  raw_name: string;
  identifier: string;
}

export interface Plaintiff {
  raw_address: string;
  raw_name: string;
  identifier: string;
  legal_representatives: LegalRepresentative[];
}

export interface Defendant {
  raw_address: string;
  raw_name: string;
  identifier: string;
  legal_representatives: LegalRepresentative[];
  addresses: object[];
}
