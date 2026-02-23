"use client";

import React, { useEffect, useState } from 'react';
import { ArrowLeft, MapPin, BarChart3, FileText, Download, RefreshCw, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { FloatingChatButton } from '@/components/floating-chat-button';

interface AnalysisData {
    site_info: {
        area_ha: number;
        area_m2: number;
        perimeter_m: number;
    };
    design_params: {
        total_area_ha: number;
        industry_focus: Array<{ type: string; percentage: number; count: number }>;
        green_ratio_target: number;
        road_width_m: number;
    };
    layout_summary: {
        total_buildings: number;
        building_counts_by_type: Record<string, number>;
        total_building_area_m2: number;
        building_area_percent: number;
        compliance_status: string;
        compliance_percent: number;
    };
    compliance: {
        status: string;
        overall_compliance_percent: number;
        violations: string[];
        recommendations: string[];
    };
}

export default function AnalysisPage() {
    const params = useParams();
    const router = useRouter();
    const estateId = params.id as string;

    const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Sample data for display
    const sampleData: AnalysisData = {
        site_info: {
            area_ha: 50.5,
            area_m2: 505000,
            perimeter_m: 2840
        },
        design_params: {
            total_area_ha: 50.5,
            industry_focus: [
                { type: 'light_manufacturing', percentage: 50, count: 15 },
                { type: 'medium_manufacturing', percentage: 20, count: 5 },
                { type: 'warehouse', percentage: 20, count: 10 },
                { type: 'support_offices', percentage: 10, count: 3 }
            ],
            green_ratio_target: 0.18,
            road_width_m: 25
        },
        layout_summary: {
            total_buildings: 33,
            building_counts_by_type: {
                light_manufacturing: 15,
                medium_manufacturing: 5,
                warehouse: 10,
                support_offices: 3
            },
            total_building_area_m2: 280000,
            building_area_percent: 55.4,
            compliance_status: 'PASS',
            compliance_percent: 92.5
        },
        compliance: {
            status: 'PASS',
            overall_compliance_percent: 92.5,
            violations: [],
            recommendations: [
                'Consider adding more green buffer zones',
                'Optimize road network for better traffic flow'
            ]
        }
    };

    useEffect(() => {
        // Try to load from sessionStorage first (from upload flow)
        const storedResult = sessionStorage.getItem('autoDesignResult');
        if (storedResult) {
            try {
                const parsed = JSON.parse(storedResult);
                // Transform API response to AnalysisData format
                const transformed: AnalysisData = {
                    site_info: parsed.site_info || sampleData.site_info,
                    design_params: {
                        total_area_ha: parsed.design_params?.total_area_ha || 0,
                        industry_focus: parsed.design_params?.industry_focus || [],
                        green_ratio_target: parsed.design_params?.green_ratio_target || 0.15,
                        road_width_m: parsed.design_params?.road_width_m || 20
                    },
                    layout_summary: parsed.layout_summary || sampleData.layout_summary,
                    compliance: parsed.compliance || sampleData.compliance
                };
                setAnalysisData(transformed);
                // Clear after loading
                sessionStorage.removeItem('autoDesignResult');
            } catch (e) {
                console.error('Failed to parse stored result:', e);
                setAnalysisData(sampleData);
            }
        } else {
            // Use sample data as fallback
            setAnalysisData(sampleData);
        }
    }, []);

    const handleRunAutoDesign = async () => {
        setIsLoading(true);
        setError(null);

        try {
            // Call MVP auto-design endpoint with sample file
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'}/api/auto-design/defaults?area_ha=50`,
                { method: 'GET' }
            );

            if (response.ok) {
                const data = await response.json();
                console.log('Auto-design defaults:', data);
            }
        } catch (err) {
            setError('Failed to run auto-design');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const data = analysisData || sampleData;

    return (
        <div className="min-h-screen flex flex-col bg-[#0a140e]">
            {/* Header */}
            <header className="w-full border-b border-[#254632] bg-[#0a140e]">
                <div className="px-6 md:px-10 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <BarChart3 className="w-8 h-8 text-primary" />
                        <h2 className="text-white text-lg font-bold">Data Analysis</h2>
                    </div>
                    <div className="flex gap-3">
                        <Button
                            variant="outline"
                            className="border-[#254632] text-white hover:bg-[#254632]"
                            onClick={() => router.back()}
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back
                        </Button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex justify-center py-6 md:py-8 px-4 md:px-10">
                <div className="w-full max-w-[1280px] flex flex-col gap-6">

                    {/* Breadcrumb */}
                    <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider">
                        <Link
                            href="/dashboard"
                            className="text-text-muted hover:text-white flex items-center gap-1 transition-colors"
                        >
                            <ArrowLeft className="w-3 h-3" />
                            Back
                        </Link>
                        <span className="text-[#557c66]">/</span>
                        <span className="text-white">{estateId}</span>
                        <span className="text-[#557c66]">/</span>
                        <span className="text-primary">Analysis</span>
                    </div>

                    {/* Page Header */}
                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                        <div className="flex flex-col gap-2">
                            <h1 className="text-white text-3xl md:text-4xl font-bold tracking-tight">
                                Site Analysis Report
                            </h1>
                            <p className="text-text-muted">
                                Automated analysis based on IEAT Thailand regulations
                            </p>
                        </div>

                        <div className="flex gap-3">
                            <Button
                                variant="outline"
                                className="border-[#254632] text-white hover:bg-[#254632]"
                                onClick={handleRunAutoDesign}
                                disabled={isLoading}
                            >
                                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                                Refresh Analysis
                            </Button>
                            <Button
                                className="bg-primary hover:bg-primary/90 text-[#0a140e] font-bold"
                                onClick={() => router.push('/upload')}
                            >
                                <Zap className="w-4 h-4 mr-2" />
                                New Auto-Design
                            </Button>
                        </div>
                    </div>

                    {/* Stats Overview */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <Card className="bg-[#121d17] border-[#254632]">
                            <CardHeader className="pb-2">
                                <CardDescription className="text-text-muted text-xs uppercase tracking-widest">
                                    Site Area
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-white">
                                    {data.site_info.area_ha.toFixed(1)} ha
                                </div>
                                <p className="text-xs text-text-muted mt-1">
                                    {data.site_info.area_m2.toLocaleString()} m²
                                </p>
                            </CardContent>
                        </Card>

                        <Card className="bg-[#121d17] border-[#254632]">
                            <CardHeader className="pb-2">
                                <CardDescription className="text-text-muted text-xs uppercase tracking-widest">
                                    Total Buildings
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-white">
                                    {data.layout_summary.total_buildings}
                                </div>
                                <p className="text-xs text-text-muted mt-1">
                                    {Object.keys(data.layout_summary.building_counts_by_type).length} types
                                </p>
                            </CardContent>
                        </Card>

                        <Card className="bg-[#121d17] border-[#254632]">
                            <CardHeader className="pb-2">
                                <CardDescription className="text-text-muted text-xs uppercase tracking-widest">
                                    Building Coverage
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-white">
                                    {data.layout_summary.building_area_percent.toFixed(1)}%
                                </div>
                                <p className="text-xs text-text-muted mt-1">
                                    of total area
                                </p>
                            </CardContent>
                        </Card>

                        <Card className="bg-[#121d17] border-[#254632]">
                            <CardHeader className="pb-2">
                                <CardDescription className="text-text-muted text-xs uppercase tracking-widest">
                                    Compliance Score
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className={`text-3xl font-bold ${data.compliance.status === 'PASS' ? 'text-primary' : 'text-yellow-500'
                                    }`}>
                                    {data.compliance.overall_compliance_percent.toFixed(1)}%
                                </div>
                                <p className={`text-xs mt-1 ${data.compliance.status === 'PASS' ? 'text-primary' : 'text-yellow-500'
                                    }`}>
                                    {data.compliance.status}
                                </p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Industry Mix */}
                    <Card className="bg-[#121d17] border-[#254632]">
                        <CardHeader>
                            <CardTitle className="text-white">Industry Distribution</CardTitle>
                            <CardDescription className="text-text-muted">
                                Building allocation by industry type
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                {data.design_params.industry_focus.map((industry, index) => (
                                    <div
                                        key={index}
                                        className="p-4 rounded-lg bg-[#0a140e] border border-[#254632]"
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-white font-medium capitalize">
                                                {industry.type.replace(/_/g, ' ')}
                                            </span>
                                            <span className="text-primary font-bold">{industry.percentage}%</span>
                                        </div>
                                        <div className="h-2 bg-[#254632] rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-primary transition-all"
                                                style={{ width: `${industry.percentage}%` }}
                                            />
                                        </div>
                                        <p className="text-xs text-text-muted mt-2">
                                            {industry.count} buildings
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Recommendations */}
                    {data.compliance.recommendations.length > 0 && (
                        <Card className="bg-[#121d17] border-[#254632]">
                            <CardHeader>
                                <CardTitle className="text-white">Recommendations</CardTitle>
                                <CardDescription className="text-text-muted">
                                    Suggestions for improvement
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-2">
                                    {data.compliance.recommendations.map((rec, index) => (
                                        <li key={index} className="flex items-start gap-3">
                                            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                                            <span className="text-white">{rec}</span>
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                        </Card>
                    )}

                    {/* Actions */}
                    <div className="flex gap-4">
                        <Button
                            variant="outline"
                            className="border-[#254632] text-white hover:bg-[#254632]"
                        >
                            <Download className="w-4 h-4 mr-2" />
                            Export Report
                        </Button>
                        <Button
                            variant="outline"
                            className="border-[#254632] text-white hover:bg-[#254632]"
                        >
                            <FileText className="w-4 h-4 mr-2" />
                            Download DXF
                        </Button>
                    </div>
                </div>
            </div>

            <FloatingChatButton projectId={estateId} />
        </div>
    );
}
