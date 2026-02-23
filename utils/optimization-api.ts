/**
 * API client for optimized subdivision and financial analysis
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface OptimizationParams {
  minPlotSize?: number;
  maxPlotSize?: number;
  targetPlotSize?: number;
  minFrontage?: number;
  maxFrontage?: number;
  targetFrontageDepthRatio?: number;
  useAdvancedOptimizer?: boolean;
  useLayoutPatterns?: boolean;
  useCPSatSolver?: boolean;
  useRoadOptimizer?: boolean;
}

export interface OptimizationResult {
  success: boolean;
  lots: any[];
  roads: any[];
  statistics: {
    total_lots: number;
    avg_quality_score: number;
    avg_rectangularity: number;
    high_quality_rate: number;
    rejection_rate: number;
  };
  geojson: any;
}

export interface FinancialMetrics {
  total_cost: number;
  total_revenue: number;
  gross_profit: number;
  roi_percentage: number;
  profit_margin: number;
  cost_breakdown: Record<string, number>;
  revenue_breakdown: any;
  cost_per_lot: number;
  revenue_per_lot: number;
  profit_per_lot: number;
}

/**
 * Run optimized subdivision algorithm on uploaded file
 */
export async function runOptimizedSubdivision(
  file: File,
  params: OptimizationParams = {}
): Promise<OptimizationResult> {
  const formData = new FormData();
  formData.append('file', file);

  // Build query parameters
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      queryParams.append(key, value.toString());
    }
  });

  const response = await fetch(
    `${API_BASE_URL}/api/optimize-subdivision?${queryParams}`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Optimization failed: ${error.detail || response.statusText}`);
  }

  return response.json();
}

/**
 * Analyze financial metrics for a design
 */
export async function analyzeFinancial(
  design: any,
  costParams?: Record<string, number>,
  revenueParams?: Record<string, number>
): Promise<{ success: boolean; metrics: FinancialMetrics; summary: any }> {
  const response = await fetch(`${API_BASE_URL}/api/financial/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      design,
      cost_params: costParams,
      revenue_params: revenueParams,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Financial analysis failed: ${error.detail || response.statusText}`);
  }

  return response.json();
}

/**
 * Compare multiple designs financially
 */
export async function compareDesigns(
  designs: any[]
): Promise<{ success: boolean; comparisons: any[]; best_design: any }> {
  const response = await fetch(`${API_BASE_URL}/api/financial/compare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ designs }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Design comparison failed: ${error.detail || response.statusText}`);
  }

  return response.json();
}

/**
 * Get default financial parameters
 */
export async function getFinancialParameters(): Promise<{
  success: boolean;
  cost_parameters: Record<string, number>;
  revenue_parameters: Record<string, number>;
}> {
  const response = await fetch(`${API_BASE_URL}/api/financial/parameters`);

  if (!response.ok) {
    throw new Error('Failed to fetch financial parameters');
  }

  return response.json();
}

/**
 * Quick financial estimate without full design
 */
export async function quickFinancialEstimate(
  totalArea: number,
  numLots: number,
  roadLength?: number,
  zoneType: string = 'FACTORY'
): Promise<{ success: boolean; estimates: any; assumptions: any }> {
  const queryParams = new URLSearchParams({
    total_area: totalArea.toString(),
    num_lots: numLots.toString(),
    zone_type: zoneType,
  });

  if (roadLength) {
    queryParams.append('road_length', roadLength.toString());
  }

  const response = await fetch(
    `${API_BASE_URL}/api/financial/quick-estimate?${queryParams}`,
    {
      method: 'POST',
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Estimation failed: ${error.detail || response.statusText}`);
  }

  return response.json();
}

/**
 * Format currency (Thai Baht)
 */
export function formatTHB(amount: number): string {
  return new Intl.NumberFormat('th-TH', {
    style: 'currency',
    currency: 'THB',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format currency in millions THB
 */
export function formatMillionTHB(amount: number): string {
  const millions = amount / 1_000_000;
  return `${millions.toFixed(1)}M THB`;
}

/**
 * Format currency in billions THB
 */
export function formatBillionTHB(amount: number): string {
  const billions = amount / 1_000_000_000;
  return `${billions.toFixed(2)}B THB`;
}

/**
 * Format percentage
 */
export function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`;
}
