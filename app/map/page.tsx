"use client";

import React from 'react';
import { SidebarNavigation } from '@/components/sidebar-navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import dynamic from 'next/dynamic';
import { Plus } from 'lucide-react';
import { FloatingChatButton } from '@/components/floating-chat-button';

const MapboxCanvas = dynamic(() => import('@/components/mapbox-canvas'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-[#0f1f18] technical-grid">
      <p className="text-white/70">Loading map...</p>
    </div>
  )
});

export default function FullScreenMapPage() {
  const projects = [
    { id: 1, name: 'KCN Tiên Sơn', status: 'active', plots: 47, area: '2,540 m²' },
    { id: 2, name: 'Sunnyvale Phase II', status: 'processing', plots: 32, area: '1,820 m²' },
    { id: 3, name: 'Industrial Park A', status: 'completed', plots: 28, area: '1,450 m²' },
  ];

  const systemLogs = [
    { timestamp: '2023-11-24 14:22:10', data: 'POLYLINE_STR_001', operation: 'Area Calculation', status: 'completed', cpu: '12.4ms' },
    { timestamp: '2023-11-24 14:20:05', data: 'BOUNDARY_L02', operation: 'Polygon Intersection', status: 'completed', cpu: '45.1ms' },
    { timestamp: '2023-11-24 14:18:32', data: 'ROAD_NETWORK_03', operation: 'Path Optimization', status: 'completed', cpu: '89.3ms' },
    { timestamp: '2023-11-24 14:15:11', data: 'BUILDING_SET_A', operation: 'Collision Detection', status: 'completed', cpu: '23.7ms' },
  ];

  return (
    <div className="h-screen overflow-hidden flex bg-[#0a1a12]">
      {/* Sidebar */}
      <SidebarNavigation />

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b border-[#1a3d2b] bg-[#0a1a12] px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Map Explorer</h1>
            <p className="text-sm text-[#D1D5DB] mt-1">Interactive DXF visualization and analysis</p>
          </div>
          <Button className="bg-primary hover:bg-primary/90 text-[#0a1a12] font-bold shadow-[0_0_20px_rgba(74,222,128,0.2)]">
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </Button>
        </header>

        {/* Content Grid */}
        <div className="flex-1 grid grid-cols-1 xl:grid-cols-3 gap-6 p-8 overflow-y-auto">
          {/* Left Column - Projects */}
          <div className="xl:col-span-1 space-y-6">
            <Card className="bg-[#11261c] border-[#1a3d2b]">
              <CardHeader>
                <CardTitle className="text-white">Active Projects</CardTitle>
                <CardDescription className="text-[#D1D5DB]">
                  Recent DXF files and estates
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {projects.map((project) => (
                  <div 
                    key={project.id}
                    className="p-4 rounded-lg bg-[#0f1f18] border border-[#1a3d2b] hover:border-primary/40 transition-all cursor-pointer glow-border"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-bold text-white">{project.name}</h3>
                      <Badge 
                        className={
                          project.status === 'active' 
                            ? 'bg-primary/20 text-primary border-primary/40' 
                            : project.status === 'processing'
                            ? 'bg-blue-500/20 text-blue-400 border-blue-500/40'
                            : 'bg-gray-500/20 text-gray-400 border-gray-500/40'
                        }
                      >
                        {project.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-[#D1D5DB]">
                      <span>{project.plots} plots</span>
                      <span className="w-1 h-1 rounded-full bg-[#1a3d2b]" />
                      <span>{project.area}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Parsing Engine Status */}
            <Card className="bg-[#11261c] border-[#1a3d2b]">
              <CardHeader>
                <CardTitle className="text-white text-sm uppercase tracking-widest">
                  Parsing Engine
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-[10px] mb-2">
                    <span className="text-[#D1D5DB]">Processing Queue</span>
                    <span className="text-primary font-mono font-bold">72%</span>
                  </div>
                  <div className="h-1 bg-[#11261c] rounded-full overflow-hidden">
                    <div className="h-full bg-primary w-[72%] transition-all duration-500" />
                  </div>
                </div>
                <div className="bg-[#0f1f18] p-4 rounded-md border border-[#1a3d2b]">
                  <p className="text-[10px] text-[#D1D5DB] leading-relaxed italic">
                    "Optimization algorithm running on KCN Tiên Sơn dataset. Geometry validation in progress..."
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Center Column - Map */}
          <div className="xl:col-span-2 space-y-6">
            <Card className="bg-[#11261c] border-[#1a3d2b] h-[500px]">
              <CardContent className="p-0 h-full">
                <div className="relative h-full rounded-lg overflow-hidden map-thumbnail">
                  <MapboxCanvas zoom={12} visibleLayers={{
                    roads: true,
                    buildings: true,
                    greenSpace: true,
                    parking: true,
                    utilities: true,
                    fireProtection: true
                  }} />
                  <div className="absolute bottom-4 left-4 glass-panel px-4 py-2 rounded-lg">
                    <div className="flex items-center gap-2">
                      <span className="size-2 bg-primary rounded-full shadow-[0_0_8px_rgba(74,222,128,1)]" />
                      <span className="text-[10px] font-black uppercase tracking-widest text-white">
                        Live Preview
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* System Logs */}
            <Card className="bg-[#11261c] border-[#1a3d2b]">
              <CardHeader className="flex flex-row items-center justify-between pb-4">
                <div>
                  <CardTitle className="text-white text-xs uppercase tracking-widest">
                    Active System Logs
                  </CardTitle>
                </div>
                <Button 
                  variant="outline" 
                  size="sm"
                  className="border-[#1a3d2b] text-white hover:bg-[#11261c]"
                >
                  Export Logs
                </Button>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-[11px]">
                    <thead className="bg-[#0a1a12] text-[#D1D5DB] uppercase font-bold">
                      <tr>
                        <th className="px-4 py-3">Timestamp</th>
                        <th className="px-4 py-3">Vector Data</th>
                        <th className="px-4 py-3">Operation</th>
                        <th className="px-4 py-3">Status</th>
                        <th className="px-4 py-3 text-right">CPU Usage</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#1a3d2b]">
                      {systemLogs.map((log, index) => (
                        <tr key={index} className="hover:bg-white/5 transition-colors">
                          <td className="px-4 py-4 font-mono text-[#D1D5DB]">{log.timestamp}</td>
                          <td className="px-4 py-4 font-bold text-white">{log.data}</td>
                          <td className="px-4 py-4 text-[#D1D5DB]">{log.operation}</td>
                          <td className="px-4 py-4">
                            <span className="text-primary font-bold flex items-center gap-1">
                              <span className="size-1.5 rounded-full bg-primary shadow-[0_0_5px_#4ade80]" />
                              COMPLETED
                            </span>
                          </td>
                          <td className="px-4 py-4 text-right font-mono text-[#D1D5DB]">{log.cpu}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
      {/* Floating Chat Button */}
      <FloatingChatButton />    </div>
  );
}
