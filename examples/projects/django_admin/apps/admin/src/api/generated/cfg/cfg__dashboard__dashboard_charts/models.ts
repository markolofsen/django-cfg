/**
 * Chart.js data structure serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ChartData {
  labels: Array<string>;
  datasets: Array<ChartDataset>;
}

/**
 * Chart.js dataset serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ChartDataset {
  label: string;
  data: Array<number>;
  backgroundColor: string;
  borderColor: string;
  tension: number;
  fill?: boolean;
}

