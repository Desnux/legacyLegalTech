export interface Metrics {
  label: string,
  llm_invocations: number,
  time: number,
  submetrics: Metrics[] | null,
}
