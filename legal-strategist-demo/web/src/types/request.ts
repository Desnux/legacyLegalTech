const DEMAND_TEXT_REQUEST_NATURES = [
  "indicate_asset_seizure_goods_for_lockdown",
  "appoint_provisional_depositary",
  "include_documents",
  "indicate_emails",
  "accredit_personality",
  "sponsorship_and_power",
  "request_exhortation",
  "cpc_notification",
  "other",
] as const;

export type DemandTextRequestNature = typeof DEMAND_TEXT_REQUEST_NATURES[number];

export type Request = { label: string, value: DemandTextRequestNature, text: string, id: string };
