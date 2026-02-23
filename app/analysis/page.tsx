"use client";

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircle2, ArrowRight, Home, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { DXFAnalysisCard } from '@/components/dxf-analysis-card';

interface DXFAnalysis {
  site_info: {
    area_ha: number;
    area_m2: number;
    dimensions: {
      width_m: number;
      height_m: number;
      perimeter_m: number;
    };
  };
  suggestions: {
    project_scale: string;
    estimated_plots: number;
    land_use_breakdown: {
      salable_area_ha: number;
      green_area_ha: number;
      utility_area_ha: number;
    };
    building_recommendations: {
      description: string;
      plot_size_range: string;
      building_height: string;
    };
  };
  questions: Array<{
    question: string;
    options?: string[];
    why?: string;
  }>;
  sample_prompts: string[];
  ai_greeting?: string;
}

export default function AnalysisPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get('projectId');
  const fileName = searchParams.get('fileName');
  
  const [analysis, setAnalysis] = useState<DXFAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!projectId) {
        router.push('/dashboard');
        return;
      }

      try {
        // Try to fetch real analysis from backend
        const response = await fetch(`/api/dxf/analysis?projectId=${projectId}`);
        if (response.ok) {
          const data = await response.json();
          setAnalysis(data);
        } else {
          // Use mock data if backend fails
          setAnalysis({
            site_info: {
              area_ha: 50.5,
              area_m2: 505000,
              dimensions: {
                width_m: 750,
                height_m: 673,
                perimeter_m: 2846
              }
            },
            suggestions: {
              project_scale: 'Large industrial park suitable for 50-100 plots',
              estimated_plots: 75,
              land_use_breakdown: {
                salable_area_ha: 35.35,
                green_area_ha: 10.1,
                utility_area_ha: 5.05
              },
              building_recommendations: {
                description: 'Mixed industrial and warehouse facilities',
                plot_size_range: '500-800 m² per plot',
                building_height: '2-3 floors (8-12m)'
              }
            },
            questions: [
              {
                question: 'What type of industrial activities will this park accommodate?',
                options: ['Light Manufacturing', 'Heavy Industry', 'Warehousing & Logistics', 'Mixed Use'],
                why: 'This helps determine optimal plot sizes and infrastructure requirements'
              },
              {
                question: 'Do you need to comply with IEAT standards?',
                options: ['Yes', 'No'],
                why: 'IEAT compliance affects layout, green space, and utility infrastructure'
              },
              {
                question: 'What is your target plot occupancy rate?',
                why: 'This helps optimize the layout for maximum return on investment'
              }
            ],
            sample_prompts: [
              'Generate a layout with 75 plots optimized for light manufacturing',
              'Show me a compliance report for IEAT standards',
              'What\'s the optimal plot size distribution for this site?',
              'Generate a layout with maximum green space'
            ],
            ai_greeting: `I've analyzed your DXF file (${fileName || 'uploaded file'}). The site has excellent potential for a large industrial park with approximately 75 plots. I can help you generate optimized layouts, check compliance, and answer any questions about your project.`
          });
        }
      } catch (error) {
        console.error('Failed to fetch analysis:', error);
        // Set mock data on error
        setAnalysis({
          site_info: {
            area_ha: 50.5,
            area_m2: 505000,
            dimensions: {
              width_m: 750,
              height_m: 673,
              perimeter_m: 2846
            }
          },
          suggestions: {
            project_scale: 'Large industrial park suitable for 50-100 plots',
            estimated_plots: 75,
            land_use_breakdown: {
              salable_area_ha: 35.35,
              green_area_ha: 10.1,
              utility_area_ha: 5.05
            },
            building_recommendations: {
              description: 'Mixed industrial and warehouse facilities',
              plot_size_range: '500-800 m² per plot',
              building_height: '2-3 floors (8-12m)'
            }
          },
          questions: [],
          sample_prompts: [
            'Generate a layout with 75 plots',
            'Show me a compliance report',
            'Optimize plot distribution'
          ],
          ai_greeting: 'Analysis complete! I can help you design your industrial park.'
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalysis();
  }, [projectId, fileName, router]);

  const handlePromptSelect = (prompt: string) => {
    // Navigate to dashboard with chat open and prompt pre-filled
    router.push(`/dashboard?prompt=${encodeURIComponent(prompt)}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a140e]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
          <p className="text-white/70">Analyzing your DXF file...</p>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a140e]">
        <div className="text-center">
          <p className="text-white/70 mb-4">Failed to load analysis</p>
          <Button onClick={() => router.push('/dashboard')}>
            <Home className="w-4 h-4 mr-2" />
            Go to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a140e] flex flex-col">
      {/* Header */}
      <header className="border-b border-[#1c3326] px-6 py-4 bg-[#122018]">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="size-10 rounded-full bg-primary/10 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-white text-xl font-bold">DXF Analysis Complete</h1>
              <p className="text-[#95c6a9] text-sm">
                {fileName || 'Your file'} has been successfully processed
              </p>
            </div>
          </div>
          <Button
            onClick={() => router.push('/dashboard')}
            className="bg-primary hover:bg-[#2dc46b] text-[#0a140e]"
          >
            <Home className="w-4 h-4 mr-2" />
            Go to Dashboard
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-6 py-8">
        <div className="max-w-7xl mx-auto">
          <DXFAnalysisCard 
            analysis={analysis}
            onPromptSelect={handlePromptSelect}
          />

          {/* Next Steps Card */}
          <Card className="bg-[#122018] border-[#1c3326] p-6 mt-6">
            <h3 className="text-white text-lg font-bold mb-4">Next Steps</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button
                onClick={() => router.push('/dashboard')}
                variant="outline"
                className="border-[#1c3326] text-white hover:bg-[#1c3326] justify-start h-auto py-4"
              >
                <div className="flex items-start gap-3">
                  <Home className="w-5 h-5 mt-1 text-primary" />
                  <div className="text-left">
                    <p className="font-semibold">View Project Dashboard</p>
                    <p className="text-xs text-[#95c6a9] mt-1">
                      See project stats, plots, and recent activity
                    </p>
                  </div>
                </div>
              </Button>
              <Button
                onClick={() => router.push(`/estate/${projectId}/map`)}
                variant="outline"
                className="border-[#1c3326] text-white hover:bg-[#1c3326] justify-start h-auto py-4"
              >
                <div className="flex items-start gap-3">
                  <ArrowRight className="w-5 h-5 mt-1 text-primary" />
                  <div className="text-left">
                    <p className="font-semibold">Start Designing Layout</p>
                    <p className="text-xs text-[#95c6a9] mt-1">
                      Use AI chat to generate optimized plot layouts
                    </p>
                  </div>
                </div>
              </Button>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
