import { Metrics } from "./metrics";

export interface Output<T> {
  metrics: Metrics
  structured_output: T | null,
}
