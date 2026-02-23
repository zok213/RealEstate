"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  LineChart,
  Line
} from 'recharts';
import { Download, TrendingUp, Award, AlertCircle } from 'lucide-react';

interface DimensionScore {
  ieat_compliance: number;
  financial_roi: number;
  lot_efficiency: number;
  infrastructure_cost: number;
  construction_timeline: number;
  customer_satisfaction: number;
  risk_assessment: number;
}

interface DesignScore {
  total_score: number;
  weighted_score: number;
  dimension_scores: DimensionScore;
  grade: string;
  weights: {
    ieat_compliance: number;
    financial_roi: number;
    lot_efficiency: number;
    infrastructure_cost: number;
    construction_timeline: number;
    customer_satisfaction: number;
    risk_assessment: number;
  };
}

interface ComparisonData {
  scores: DesignScore[];
  best_overall: number;
  best_by_dimension: Record<string, number>;
  comparison_matrix: {
    designs: Array<{
      id: number;
      name: string;
      weighted_score: number;
      grade: string;
    }>;
    dimensions: Record<string, number[]>;
  };
}

interface SensitivityData {
  parameter: string;
  values: number[];
  scores: number[];
  optimal_value: number;
  optimal_score: number;
  score_delta: number;
}

const COLORS = {
  primary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  purple: '#8b5cf6',
  pink: '#ec4899',
  cyan: '#06b6d4'
};

const DIMENSION_COLORS = [
  COLORS.primary,
  COLORS.success,
  COLORS.warning,
  COLORS.purple,
  COLORS.pink,
  COLORS.cyan,
  '#64748b'
];

const DIMENSION_LABELS: Record<string, string> = {
  ieat_compliance: 'IEAT Compliance',
  financial_roi: 'Financial ROI',
  lot_efficiency: 'Lot Efficiency',
  infrastructure_cost: 'Infrastructure Cost',
  construction_timeline: 'Construction Timeline',
  customer_satisfaction: 'Customer Satisfaction',
  risk_assessment: 'Risk Assessment'
};

export default function ScoringMatrixDashboard() {
  const [activeDesign, setActiveDesign] = useState<DesignScore | null>(null);
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [sensitivity, setSensitivity] = useState<SensitivityData | null>(null);
  const [selectedParameter, setSelectedParameter] = useState('salable_area_pct');
  const [loading, setLoading] = useState(false);

  // Load single design score
  const loadDesignScore = async (designId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/scoring/score-design`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design_id: designId })
      });
      const data = await response.json();
      setActiveDesign(data);
    } catch (error) {
      console.error('Failed to load design score:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load design comparison
  const loadComparison = async (designIds: string[]) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/scoring/compare-designs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design_ids: designIds })
      });
      const data = await response.json();
      setComparison(data);
    } catch (error) {
      console.error('Failed to load comparison:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load sensitivity analysis
  const loadSensitivity = async (designId: string, parameter: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/scoring/sensitivity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          design_id: designId,
          parameter,
          value_range: [0.6, 0.9],
          num_steps: 15
        })
      });
      const data = await response.json();
      setSensitivity(data);
    } catch (error) {
      console.error('Failed to load sensitivity:', error);
    } finally {
      setLoading(false);
    }
  };

  // Export to PDF
  const exportToPDF = () => {
    // Implement PDF export using jsPDF or similar
    console.log('Exporting to PDF...');
  };

  // Prepare data for charts
  const getDimensionChartData = (scores: DimensionScore) => {
    return Object.entries(scores).map(([key, value]) => ({
      dimension: DIMENSION_LABELS[key] || key,
      score: value,
      shortName: key
    }));
  };

  const getRadarChartData = (scores: DimensionScore) => {
    return Object.entries(scores).map(([key, value]) => ({
      dimension: DIMENSION_LABELS[key]?.split(' ')[0] || key,
      value: value,
      fullMark: 100
    }));
  };

  const getSensitivityChartData = (sensitivity: SensitivityData) => {
    return sensitivity.values.map((value, index) => ({
      value: value,
      score: sensitivity.scores[index]
    }));
  };

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return COLORS.success;
    if (grade.startsWith('B')) return COLORS.primary;
    if (grade.startsWith('C')) return COLORS.warning;
    return COLORS.danger;
  };

  return (
    <div className="w-full space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Design Scoring Matrix</h2>
          <p className="text-muted-foreground">
            Comprehensive evaluation across 7 key dimensions
          </p>
        </div>
        <Button onClick={exportToPDF} className="gap-2">
          <Download className="h-4 w-4" />
          Export PDF
        </Button>
      </div>

      <Tabs defaultValue="single" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="single">Single Design</TabsTrigger>
          <TabsTrigger value="comparison">Compare Designs</TabsTrigger>
          <TabsTrigger value="sensitivity">Sensitivity Analysis</TabsTrigger>
        </TabsList>

        {/* SINGLE DESIGN TAB */}
        <TabsContent value="single" className="space-y-6">
          {activeDesign && (
            <>
              {/* Score Summary */}
              <div className="grid gap-4 md:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Weighted Score</CardTitle>
                    <Award className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{activeDesign.weighted_score.toFixed(1)}</div>
                    <p className="text-xs text-muted-foreground">out of 100</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Grade</CardTitle>
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <Badge
                      className="text-2xl font-bold px-4 py-2"
                      style={{ backgroundColor: getGradeColor(activeDesign.grade) }}
                    >
                      {activeDesign.grade}
                    </Badge>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Score</CardTitle>
                    <AlertCircle className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{activeDesign.total_score.toFixed(1)}</div>
                    <p className="text-xs text-muted-foreground">unweighted average</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Top Dimension</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-sm font-bold">
                      {Object.entries(activeDesign.dimension_scores)
                        .sort(([, a], [, b]) => b - a)[0][0]
                        .split('_')
                        .map(w => w[0].toUpperCase() + w.slice(1))
                        .join(' ')}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {Object.values(activeDesign.dimension_scores).sort((a, b) => b - a)[0].toFixed(1)}/100
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Charts */}
              <div className="grid gap-6 md:grid-cols-2">
                {/* Bar Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle>Dimension Breakdown</CardTitle>
                    <CardDescription>Score by evaluation dimension</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={getDimensionChartData(activeDesign.dimension_scores)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="dimension" angle={-45} textAnchor="end" height={120} fontSize={12} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Bar dataKey="score" fill={COLORS.primary}>
                          {getDimensionChartData(activeDesign.dimension_scores).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={DIMENSION_COLORS[index]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* Radar Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle>Performance Profile</CardTitle>
                    <CardDescription>Multidimensional assessment radar</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <RadarChart data={getRadarChartData(activeDesign.dimension_scores)}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="dimension" />
                        <PolarRadiusAxis domain={[0, 100]} />
                        <Radar
                          name="Score"
                          dataKey="value"
                          stroke={COLORS.primary}
                          fill={COLORS.primary}
                          fillOpacity={0.6}
                        />
                        <Tooltip />
                      </RadarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* Pie Chart - Weights */}
                <Card>
                  <CardHeader>
                    <CardTitle>Weight Distribution</CardTitle>
                    <CardDescription>How dimensions are weighted in final score</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={Object.entries(activeDesign.weights).map(([key, value]) => ({
                            name: DIMENSION_LABELS[key],
                            value: value * 100
                          }))}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name.split(' ')[0]} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {Object.keys(activeDesign.weights).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={DIMENSION_COLORS[index]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* Detailed Scores Table */}
                <Card>
                  <CardHeader>
                    <CardTitle>Detailed Scores</CardTitle>
                    <CardDescription>Individual dimension performance</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(activeDesign.dimension_scores).map(([key, score], index) => (
                        <div key={key} className="flex items-center gap-4">
                          <div
                            className="h-3 w-3 rounded-full"
                            style={{ backgroundColor: DIMENSION_COLORS[index] }}
                          />
                          <div className="flex-1">
                            <div className="text-sm font-medium">{DIMENSION_LABELS[key]}</div>
                            <div className="h-2 w-full bg-secondary rounded-full mt-1">
                              <div
                                className="h-full rounded-full transition-all"
                                style={{
                                  width: `${score}%`,
                                  backgroundColor: DIMENSION_COLORS[index]
                                }}
                              />
                            </div>
                          </div>
                          <div className="text-sm font-bold tabular-nums">{score.toFixed(1)}</div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* COMPARISON TAB */}
        <TabsContent value="comparison" className="space-y-6">
          {comparison && (
            <>
              {/* Summary Cards */}
              <div className="grid gap-4 md:grid-cols-3">
                {comparison.comparison_matrix.designs.map((design, index) => (
                  <Card
                    key={design.id}
                    className={
                      index === comparison.best_overall
                        ? 'border-2 border-green-500'
                        : ''
                    }
                  >
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        {design.name}
                        {index === comparison.best_overall && (
                          <Badge variant="default" className="bg-green-500">Best Overall</Badge>
                        )}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Score</span>
                          <span className="text-2xl font-bold">{design.weighted_score.toFixed(1)}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Grade</span>
                          <Badge style={{ backgroundColor: getGradeColor(design.grade) }}>
                            {design.grade}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Comparison Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Side-by-Side Comparison</CardTitle>
                  <CardDescription>Compare all dimensions across designs</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                      data={Object.entries(comparison.comparison_matrix.dimensions).map(([dim, scores]) => ({
                        dimension: DIMENSION_LABELS[dim],
                        ...comparison.comparison_matrix.designs.reduce((acc, design, idx) => ({
                          ...acc,
                          [design.name]: scores[idx]
                        }), {})
                      }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="dimension" angle={-45} textAnchor="end" height={120} fontSize={12} />
                      <YAxis domain={[0, 100]} />
                      <Tooltip />
                      <Legend />
                      {comparison.comparison_matrix.designs.map((design, idx) => (
                        <Bar
                          key={design.id}
                          dataKey={design.name}
                          fill={DIMENSION_COLORS[idx]}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* SENSITIVITY TAB */}
        <TabsContent value="sensitivity" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Sensitivity Analysis</CardTitle>
              <CardDescription>
                Analyze how design score changes with parameter variations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium">Parameter:</label>
                <select
                  className="flex h-10 w-full max-w-xs rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={selectedParameter}
                  onChange={(e) => setSelectedParameter(e.target.value)}
                >
                  <option value="salable_area_pct">Salable Area %</option>
                  <option value="green_space_pct">Green Space %</option>
                  <option value="lot_count">Lot Count</option>
                  <option value="road_row_m">Road ROW (m)</option>
                </select>
                <Button
                  onClick={() => activeDesign && loadSensitivity('current', selectedParameter)}
                  disabled={loading}
                >
                  Analyze
                </Button>
              </div>

              {sensitivity && (
                <>
                  {/* Optimal Value Card */}
                  <Card className="bg-muted">
                    <CardContent className="pt-6">
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <p className="text-sm text-muted-foreground">Optimal Value</p>
                          <p className="text-2xl font-bold">{sensitivity.optimal_value.toFixed(3)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Optimal Score</p>
                          <p className="text-2xl font-bold">{sensitivity.optimal_score.toFixed(1)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Score Delta</p>
                          <p className={`text-2xl font-bold ${sensitivity.score_delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {sensitivity.score_delta >= 0 ? '+' : ''}{sensitivity.score_delta.toFixed(1)}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Sensitivity Chart */}
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={getSensitivityChartData(sensitivity)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="value"
                        label={{ value: sensitivity.parameter, position: 'insideBottom', offset: -5 }}
                      />
                      <YAxis label={{ value: 'Score', angle: -90, position: 'insideLeft' }} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="score"
                        stroke={COLORS.primary}
                        strokeWidth={3}
                        dot={{ fill: COLORS.primary, r: 5 }}
                        activeDot={{ r: 8 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
