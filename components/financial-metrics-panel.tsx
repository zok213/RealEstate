/**
 * Financial Metrics Display Panel
 * 
 * Shows comprehensive financial analysis including:
 * - ROI and profitability metrics
 * - Cost breakdown
 * - Revenue analysis
 * - Comparison charts
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatBillionTHB, formatMillionTHB, formatPercentage } from '@/utils/optimization-api';
import type { FinancialMetrics } from '@/utils/optimization-api';

interface FinancialMetricsPanelProps {
  metrics: FinancialMetrics | null;
  loading?: boolean;
}

export function FinancialMetricsPanel({ metrics, loading }: FinancialMetricsPanelProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Financial Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!metrics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Financial Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">
            Generate a design to see financial metrics
          </p>
        </CardContent>
      </Card>
    );
  }

  const isProfitable = metrics.gross_profit > 0;
  const roiColor = metrics.roi_percentage >= 25 ? 'text-green-600' : 
                   metrics.roi_percentage >= 15 ? 'text-yellow-600' : 'text-red-600';

  return (
    <div className="space-y-4">
      {/* Key Metrics Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Financial Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <MetricCard
              label="Total Cost"
              value={formatBillionTHB(metrics.total_cost)}
              subValue={`${formatMillionTHB(metrics.cost_per_lot)} per lot`}
              variant="neutral"
            />
            <MetricCard
              label="Total Revenue"
              value={formatBillionTHB(metrics.total_revenue)}
              subValue={`${formatMillionTHB(metrics.revenue_per_lot)} per lot`}
              variant="neutral"
            />
            <MetricCard
              label="Gross Profit"
              value={formatBillionTHB(metrics.gross_profit)}
              subValue={`${formatMillionTHB(metrics.profit_per_lot)} per lot`}
              variant={isProfitable ? 'success' : 'danger'}
            />
            <MetricCard
              label="ROI"
              value={formatPercentage(metrics.roi_percentage)}
              subValue={`Margin: ${formatPercentage(metrics.profit_margin)}`}
              variant={metrics.roi_percentage >= 25 ? 'success' : metrics.roi_percentage >= 15 ? 'warning' : 'danger'}
            />
          </div>

          {/* Profitability Indicator */}
          <div className="mt-6">
            <ProfitabilityIndicator roi={metrics.roi_percentage} />
          </div>
        </CardContent>
      </Card>

      {/* Cost Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Cost Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <CostBreakdownList breakdown={metrics.cost_breakdown} total={metrics.total_cost} />
        </CardContent>
      </Card>

      {/* Revenue Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Revenue Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Number of Lots:</span>
              <span className="font-medium">{metrics.revenue_breakdown.num_lots}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Avg Price per m²:</span>
              <span className="font-medium">
                {formatMillionTHB(metrics.revenue_breakdown.avg_price_per_m2)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
  subValue?: string;
  variant: 'success' | 'danger' | 'warning' | 'neutral';
}

function MetricCard({ label, value, subValue, variant }: MetricCardProps) {
  const variantStyles = {
    success: 'bg-green-50 border-green-200',
    danger: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
    neutral: 'bg-gray-50 border-gray-200',
  };

  const textStyles = {
    success: 'text-green-700',
    danger: 'text-red-700',
    warning: 'text-yellow-700',
    neutral: 'text-gray-700',
  };

  return (
    <div className={`p-4 rounded-lg border ${variantStyles[variant]}`}>
      <div className="text-sm text-muted-foreground mb-1">{label}</div>
      <div className={`text-2xl font-bold ${textStyles[variant]}`}>{value}</div>
      {subValue && (
        <div className="text-xs text-muted-foreground mt-1">{subValue}</div>
      )}
    </div>
  );
}

interface CostBreakdownListProps {
  breakdown: Record<string, number>;
  total: number;
}

function CostBreakdownList({ breakdown, total }: CostBreakdownListProps) {
  const items = [
    { key: 'site_clearing', label: 'Site Clearing' },
    { key: 'grading', label: 'Grading' },
    { key: 'roads', label: 'Road Construction' },
    { key: 'water_pipes', label: 'Water Pipes' },
    { key: 'sewer_pipes', label: 'Sewer Pipes' },
    { key: 'electric_cables', label: 'Electric Cables' },
    { key: 'utility_connections', label: 'Utility Connections' },
    { key: 'landscaping', label: 'Landscaping' },
    { key: 'tree_planting', label: 'Tree Planting' },
    { key: 'design_fee', label: 'Design Fee' },
    { key: 'contingency', label: 'Contingency' },
  ];

  return (
    <div className="space-y-2">
      {items.map(({ key, label }) => {
        const amount = breakdown[key] || 0;
        const percentage = (amount / total) * 100;
        
        if (amount === 0) return null;

        return (
          <div key={key} className="flex items-center gap-3">
            <div className="flex-1">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">{label}</span>
                <span className="font-medium">{formatMillionTHB(amount)}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                />
              </div>
            </div>
            <span className="text-xs text-muted-foreground w-12 text-right">
              {percentage.toFixed(1)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

interface ProfitabilityIndicatorProps {
  roi: number;
}

function ProfitabilityIndicator({ roi }: ProfitabilityIndicatorProps) {
  let status: 'excellent' | 'good' | 'fair' | 'poor';
  let message: string;
  let color: string;

  if (roi >= 40) {
    status = 'excellent';
    message = 'Excellent ROI - Highly profitable project';
    color = 'bg-green-500';
  } else if (roi >= 25) {
    status = 'good';
    message = 'Good ROI - Project meets investment targets';
    color = 'bg-green-400';
  } else if (roi >= 15) {
    status = 'fair';
    message = 'Fair ROI - Consider cost optimization';
    color = 'bg-yellow-500';
  } else {
    status = 'poor';
    message = 'Low ROI - Significant optimization needed';
    color = 'bg-red-500';
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Project Viability</span>
        <span className={`text-sm font-semibold ${
          status === 'excellent' || status === 'good' ? 'text-green-600' :
          status === 'fair' ? 'text-yellow-600' : 'text-red-600'
        }`}>
          {status.toUpperCase()}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`${color} h-3 rounded-full transition-all`}
          style={{ width: `${Math.min((roi / 50) * 100, 100)}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground">{message}</p>
      
      {/* ROI Reference Scale */}
      <div className="mt-4 pt-4 border-t">
        <div className="text-xs text-muted-foreground mb-2">ROI Reference Scale</div>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-green-500" />
            <span>&gt;40% - Excellent</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-green-400" />
            <span>25-40% - Good (Target Range)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-yellow-500" />
            <span>15-25% - Fair</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-red-500" />
            <span>&lt;15% - Poor</span>
          </div>
        </div>
      </div>
    </div>
  );
}
