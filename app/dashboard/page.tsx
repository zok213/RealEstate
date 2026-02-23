"use client";

import React, { useEffect, useState } from 'react';
import { ArrowLeft, MapPin, Copy, Settings, Plus, FileText, Map, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FloatingChatButton } from '@/components/floating-chat-button';
import { cn } from '@/lib/utils';

interface DashboardData {
  project: {
    id: string;
    name: string;
    location: string;
    total_area: number;
    total_plots: number;
    estimated_value: number;
    last_updated: string;
  };
  stats: {
    available_plots: number;
    reserved_plots: number;
    sold_plots: number;
  };
  recent_activity: Array<{
    id: string;
    action: string;
    description: string;
    timestamp: string;
    status: 'completed' | 'processing' | 'failed';
  }>;
}

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch('/api/dashboard?projectId=kcn-tien-son');
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a140e]">
        <div className="text-center">
          <div className="size-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/70">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a140e]">
        <p className="text-white/70">Failed to load dashboard</p>
      </div>
    );
  }

  const { project, stats, recent_activity } = data;

  return (
    <div className="min-h-screen flex flex-col bg-[#0a140e]">
      {/* Header */}
      <header className="w-full border-b border-[#254632] bg-[#0a140e]">
        <div className="px-6 md:px-10 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="size-8 flex items-center justify-center text-primary">
              <Map className="w-8 h-8" />
            </div>
            <h2 className="text-white text-lg font-bold leading-tight tracking-tight">
              DXF Parser
            </h2>
          </div>
          <div className="flex flex-1 justify-end gap-8 items-center">
            <nav className="hidden md:flex items-center gap-9">
              <Link 
                href="/dashboard" 
                className="text-text-muted hover:text-primary transition-colors text-sm font-medium"
              >
                Dashboard
              </Link>
              <Link 
                href="/dashboard" 
                className="text-primary glow-green text-sm font-bold border-b-2 border-primary pt-1 pb-1"
              >
                Estates
              </Link>
              <Link 
                href="/settings" 
                className="text-text-muted hover:text-primary transition-colors text-sm font-medium"
              >
                Settings
              </Link>
            </nav>
            <button className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-[#121d17] border border-[#254632] hover:bg-[#254632] transition-colors">
              <Settings className="text-white w-5 h-5" />
            </button>
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
            <Link href="/dashboard" className="text-text-muted hover:text-white transition-colors">
              Estates
            </Link>
            <span className="text-[#557c66]">/</span>
            <span className="text-white">KCN Tiên Sơn</span>
          </div>

          {/* Page Header */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div className="flex flex-col gap-2">
              <h1 className="text-white text-3xl md:text-4xl font-bold tracking-tight">
                {project.name}
              </h1>
              <div className="flex items-center gap-3 text-text-muted">
                <span className="flex items-center gap-1.5 text-sm">
                  <MapPin className="w-4 h-4" />
                  {project.location}
                </span>
                <span className="w-1 h-1 rounded-full bg-[#254632]"></span>
                <span className="text-sm font-mono text-text-dim flex items-center gap-2">
                  ID: {project.id}
                  <button className="hover:text-primary transition-colors" title="Copy ID">
                    <Copy className="w-3 h-3" />
                  </button>
                </span>
              </div>
            </div>
            
            <div className="flex gap-3">
              <Button 
                variant="outline"
                className="border-[#254632] text-white hover:bg-[#254632]"
              >
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
              <Button 
                className="bg-primary hover:bg-primary/90 text-[#0a140e] font-bold shadow-[0_0_20px_rgba(54,226,123,0.2)]"                onClick={() => router.push('/upload')}              >
                <Plus className="w-4 h-4 mr-2" />
                New Analysis
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-[#121d17] border-[#254632]">
              <CardHeader className="pb-2">
                <CardDescription className="text-text-muted text-xs uppercase tracking-widest">
                  Total Area
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-white">{project.total_area.toLocaleString()} m²</div>
                <p className="text-xs text-text-muted mt-1">Buildable land</p>
              </CardContent>
            </Card>

            <Card className="bg-[#121d17] border-[#254632]">
              <CardHeader className="pb-2">
                <CardDescription className="text-text-muted text-xs uppercase tracking-widest">
                  Total Plots
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-white">{project.total_plots}</div>
                <p className="text-xs text-text-muted mt-1">
                  <span className="text-primary">{stats.available_plots} Available</span> • {stats.sold_plots} Sold
                </p>
              </CardContent>
            </Card>

            <Card className="bg-[#121d17] border-[#254632]">
              <CardHeader className="pb-2">
                <CardDescription className="text-text-muted text-xs uppercase tracking-widest">
                  Est. Value
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-white">
                  ${(project.estimated_value / 1000000).toFixed(1)}M
                </div>
                <p className="text-xs text-primary mt-1">+8.2% from last quarter</p>
              </CardContent>
            </Card>

            <Card className="bg-[#121d17] border-[#254632]">
              <CardHeader className="pb-2">
                <CardDescription className="text-text-muted text-xs uppercase tracking-widest">
                  Last Updated
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-white">
                  {new Date(project.last_updated).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
                <p className="text-xs text-text-muted mt-1">
                  {new Date(project.last_updated).toLocaleString('en-US', { 
                    month: 'short', 
                    day: 'numeric', 
                    year: 'numeric',
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/estate/kcn-tien-son/map">
              <Card className="bg-[#121d17] border-[#254632] hover:border-primary transition-all cursor-pointer group">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-lg bg-primary/10 border border-primary/20 group-hover:border-primary/40 transition-all">
                      <Map className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-white text-lg">Technical Map</CardTitle>
                      <CardDescription className="text-text-muted">
                        View interactive CAD layout
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            </Link>

            <Link href="/estate/kcn-tien-son/plots">
              <Card className="bg-[#121d17] border-[#254632] hover:border-primary transition-all cursor-pointer group">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-lg bg-primary/10 border border-primary/20 group-hover:border-primary/40 transition-all">
                      <FileText className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-white text-lg">Plot Inventory</CardTitle>
                      <CardDescription className="text-text-muted">
                        Manage plots and sales data
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            </Link>

            <Link href="/estate/kcn-tien-son/analysis">
              <Card className="bg-[#121d17] border-[#254632] hover:border-primary transition-all cursor-pointer group">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-lg bg-primary/10 border border-primary/20 group-hover:border-primary/40 transition-all">
                      <BarChart3 className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-white text-lg">Data Analysis</CardTitle>
                      <CardDescription className="text-text-muted">
                        View insights and reports
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            </Link>
          </div>

          {/* Recent Activity */}
          <Card className="bg-[#121d17] border-[#254632]">
            <CardHeader>
              <CardTitle className="text-white">Recent Activity</CardTitle>
              <CardDescription className="text-text-muted">
                Latest changes to this estate
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { action: 'DXF file uploaded', time: '2 days ago', status: 'success' },
                  { action: 'Plot P-042 marked as sold', time: '5 days ago', status: 'info' },
                  { action: 'Boundary analysis completed', time: '1 week ago', status: 'success' },
                  { action: 'New subdivision layout generated', time: '2 weeks ago', status: 'info' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between py-2 border-b border-[#254632] last:border-0">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${
                        item.status === 'success' ? 'bg-primary' : 'bg-blue-500'
                      }`} />
                      <span className="text-white text-sm">{item.action}</span>
                    </div>
                    <span className="text-text-muted text-xs">{item.time}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Floating Chat Button */}
      <FloatingChatButton projectId="kcn-tien-son" />
    </div>
  );
}
