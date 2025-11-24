export interface PreliminaryMeasureInputInformation {
  city: string | null,
  total_transaction_amount: number | null,
  claimed_transactions: Record<string, any>[] | null,
  measure_information: Record<string, any> | null,
  claimant_partner: Record<string, any> | null,
  claimant_request: Record<string, any> | null,
}
