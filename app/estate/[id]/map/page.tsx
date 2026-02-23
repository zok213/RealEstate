"use client";

import React, { useState, useEffect } from 'react';
import { 
  X, 
  ZoomIn, 
  ZoomOut, 
  Navigation, 
  Layers,
  MapPin,
  Square,
  Loader2
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import dynamic from 'next/dynamic';
import { FloatingChatButton } from '@/components/floating-chat-button';

// Dynamic import for map to avoid SSR issues
const MapboxCanvas = dynamic(() => import('@/components/mapbox-canvas'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center technical-grid">
      <p className="text-white/70">Loading map...</p>
    </div>
  )
});

interface PlotData {
  id: string;
  name: string;
  status: 'available' | 'reserved' | 'sold';
  area: number;
  price: number;
  pricePerSqm: number;
  coordinates: string;
  zoning: string;
  location: string;
  buyer?: string;
  details?: {
    buildingCoverage: number;
    maxHeight: string;
    utilities: string[];
    accessRoad: string;
    soilType: string;
  };
}

export default function MapViewPage({ params }: { params: { id: string } }) {
  const [selectedPlot, setSelectedPlot] = useState<PlotData | null>(null);
  const [isLoadingPlot, setIsLoadingPlot] = useState(false);
  const [hoveredPlotId, setHoveredPlotId] = useState<string | null>(null);

  // Fetch initial plot on mount
  useEffect(() => {
    handlePlotClick('P-042');
  }, []);

  const handlePlotClick = async (plotId: string) => {
    setIsLoadingPlot(true);
    try {
      const response = await fetch(`/api/plots/${params.id}/${plotId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedPlot(data);
      }
    } catch (error) {
      console.error('Failed to fetch plot details:', error);
    } finally {
      setIsLoadingPlot(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-primary text-[#0a130e]';
      case 'reserved': return 'bg-[#f97316] text-white';
      case 'sold': return 'bg-[#64748b] text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-[#0a130e]">
      {/* Header */}
      <header className="flex-none flex items-center justify-between border-b border-[#1c3326] px-6 py-3 bg-[#0a130e] z-30">
        <div className="flex items-center gap-4">
          <div className="size-8 text-primary">
            <MapPin className="w-full h-full" />
          </div>
          <h2 className="text-white text-lg font-bold tracking-tight">EstateParser</h2>
        </div>
        <div className="flex items-center gap-6">
          <nav className="hidden md:flex items-center gap-6">
            <Link href="/dashboard" className="text-white/70 hover:text-white text-sm font-medium transition-colors">
              Dashboard
            </Link>
            <Link href="#" className="text-white/70 hover:text-white text-sm font-medium transition-colors">
              Engineering
            </Link>
            <Link href="#" className="text-white/70 hover:text-white text-sm font-medium transition-colors">
              Analysis
            </Link>
          </nav>
          <div className="h-6 w-px bg-[#1c3326] mx-2"></div>
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full size-10 hover:bg-[#122018]"
          >
            <span className="size-2 bg-primary rounded-full absolute top-2 right-2 border-2 border-[#0a130e]" />
            <span className="material-symbols-outlined text-[20px]">notifications</span>
          </Button>
          <div className="bg-center bg-no-repeat bg-cover rounded-full size-9 border border-[#1c3326] cursor-pointer bg-[#122018]" />
        </div>
      </header>

      {/* Breadcrumb Tabs */}
      <div className="flex-none bg-[#0a130e] border-b border-[#1c3326] z-20">
        <div className="px-6 pt-3 pb-0">
          <div className="flex flex-wrap items-center gap-2 text-xs mb-3">
            <span className="text-white/50 uppercase tracking-widest font-bold">Project /</span>
            <span className="text-white font-medium uppercase tracking-widest">Sunnyvale Phase II</span>
          </div>
          <div className="flex gap-8">
            <Link href="/dashboard" className="group border-b-2 border-transparent hover:border-white/20 pb-2.5 transition-all">
              <p className="text-white/50 group-hover:text-white text-xs font-bold uppercase tracking-widest">Overview</p>
            </Link>
            <Link href={`/estate/${params.id}/map`} className="border-b-2 border-primary pb-2.5">
              <p className="text-primary text-xs font-bold uppercase tracking-widest">Technical Map</p>
            </Link>
            <Link href={`/estate/${params.id}/plots`} className="group border-b-2 border-transparent hover:border-white/20 pb-2.5 transition-all">
              <p className="text-white/50 group-hover:text-white text-xs font-bold uppercase tracking-widest">Inventory</p>
            </Link>
            <Link href="#" className="group border-b-2 border-transparent hover:border-white/20 pb-2.5 transition-all">
              <p className="text-white/50 group-hover:text-white text-xs font-bold uppercase tracking-widest">DXF Layers</p>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Map Content */}
      <main className="flex-1 relative overflow-hidden technical-grid">
        {/* Map Canvas */}
        <div 
          className="absolute inset-0 cursor-crosshair"
          onClick={(e) => {
            // Simulate plot click - in real implementation, this would use map coordinates
            const plots = ['P-001', 'P-042', 'P-003'];
            const randomPlot = plots[Math.floor(Math.random() * plots.length)];
            handlePlotClick(randomPlot);
          }}
        >
          <MapboxCanvas zoom={15} visibleLayers={{
            roads: true,
            buildings: true,
            greenSpace: true,
            parking: true,
            utilities: true,
            fireProtection: true
          }} />
        </div>

        {/* Plot Details Glass Panel - Right Side */}
        {selectedPlot && (
          <div className="absolute top-6 right-6 z-10 pointer-events-auto">
            <div className="relative">
              <div className="glass-panel rounded-lg shadow-2xl max-w-xs overflow-hidden">
                {/* Panel Header */}
                <div className="bg-primary/90 backdrop-blur-xl px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Square className="w-5 h-5 text-[#0a130e]" />
                    <p className="text-[#0a130e]/80 text-[10px] font-black uppercase tracking-[0.1em]">
                      Engineering Specs
                    </p>
                  </div>
                  <button 
                    onClick={() => setSelectedPlot(null)}
                    className="size-8 rounded-full bg-[#0a130e]/20 hover:bg-[#0a130e]/30 flex items-center justify-center transition-colors"
                  >
                    <X className="text-[#0a130e] w-5 h-5" />
                  </button>
                </div>

                {/* Panel Content */}
                <div className="p-6 space-y-5 bg-[#122018]">
                  {isLoadingPlot ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-8 h-8 text-primary animate-spin" />
                    </div>
                  ) : (
                    <>
                      {/* Plot Title */}
                      <div className="space-y-2">
                        <h3 className="text-xl font-bold text-white">{selectedPlot.name || `Plot ${selectedPlot.id}`}</h3>
                        {selectedPlot.location && (
                          <p className="text-sm text-white/70">{selectedPlot.location}</p>
                        )}
                      </div>

                      {/* Main Stats Grid */}
                      <div className="grid grid-cols-2 gap-y-5 gap-x-6">
                        <div className="space-y-1.5">
                          <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60">
                            Total Area
                          </p>
                          <p className="text-lg font-bold text-white tracking-tight leading-none">
                            {selectedPlot.area.toFixed(2)} m²
                          </p>
                        </div>
                        <div className="space-y-1.5">
                          <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60">
                            Total Price
                          </p>
                          <p className="text-lg font-bold text-white tracking-tight leading-none">
                            ${selectedPlot.price.toLocaleString()}
                          </p>
                        </div>
                        <div className="space-y-1.5">
                          <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60">
                            Price/m²
                          </p>
                          <p className="text-lg font-bold text-white tracking-tight leading-none">
                            ${selectedPlot.pricePerSqm}
                          </p>
                        </div>
                        <div className="space-y-1.5">
                          <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60">
                            Zoning Code
                          </p>
                          <p className="text-sm font-bold text-white tracking-tight">
                            {selectedPlot.zoning}
                          </p>
                        </div>
                        <div className="space-y-1.5 col-span-2">
                          <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60">
                            Coordinates
                          </p>
                          <p className="text-[12px] font-mono text-primary font-bold">
                            {selectedPlot.coordinates}
                          </p>
                        </div>
                      </div>

                      {/* Buyer Info (if exists) */}
                      {selectedPlot.buyer && (
                        <div className="pt-3 border-t border-white/10">
                          <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60 mb-2">
                            Buyer
                          </p>
                          <p className="text-sm text-white font-medium">{selectedPlot.buyer}</p>
                        </div>
                      )}

                      {/* Technical Details (if exists) */}
                      {selectedPlot.details && (
                        <div className="pt-3 border-t border-white/10 space-y-4">
                          <p className="text-xs font-bold text-white/70 uppercase tracking-widest">
                            Technical Details
                          </p>
                          <div className="space-y-3">
                            <div>
                              <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60 mb-1">
                                Building Coverage
                              </p>
                              <p className="text-sm text-white">{selectedPlot.details.buildingCoverage}%</p>
                            </div>
                            <div>
                              <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60 mb-1">
                                Max Height
                              </p>
                              <p className="text-sm text-white">{selectedPlot.details.maxHeight}</p>
                            </div>
                            <div>
                              <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60 mb-2">
                                Utilities
                              </p>
                              <div className="flex flex-wrap gap-1.5">
                                {selectedPlot.details.utilities.map((utility, idx) => (
                                  <Badge 
                                    key={idx} 
                                    className="bg-primary/20 text-primary border-primary/40 text-[10px] px-2 py-0.5"
                                  >
                                    {utility}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            <div>
                              <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60 mb-1">
                                Access Road
                              </p>
                              <p className="text-sm text-white">{selectedPlot.details.accessRoad}</p>
                            </div>
                            <div>
                              <p className="text-[9px] font-black uppercase tracking-[0.25em] text-white/60 mb-1">
                                Soil Type
                              </p>
                              <p className="text-sm text-white">{selectedPlot.details.soilType}</p>
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="pt-4 border-t border-white/10">
                        <div className="flex justify-between items-center mb-5">
                          <span className="text-xs font-bold text-white/70 uppercase tracking-widest">
                            Current Status
                          </span>
                          <Badge className={`${getStatusColor(selectedPlot.status)} px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg`}>
                            {selectedPlot.status}
                          </Badge>
                        </div>
                        <Button 
                          className="w-full bg-primary hover:bg-white text-[#0a130e] font-black py-4 rounded-lg text-xs uppercase tracking-[0.25em] transition-all flex items-center justify-center gap-2 shadow-[0_10px_30px_-5px_rgba(54,226,123,0.4)]"
                          onClick={() => window.location.href = `/estate/${params.id}/plots`}
                        >
                          <span>View Full Details</span>
                        </Button>
                      </div>
                    </>
                  )}
                </div>

                {/* Pointer Triangle */}
                <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 glass-panel bg-[#122018] border-r border-b border-primary/30 rotate-45 border-t-0 border-l-0"></div>
              </div>
            </div>
          </div>
        )}

        {/* Bottom Controls */}
        <div className="absolute bottom-6 left-6 right-6 flex justify-between items-end pointer-events-auto z-20">
          {/* Status Bar */}
          <div className="glass-panel rounded-lg px-4 py-2.5 flex items-center gap-4 shadow-xl">
            <div className="flex items-center gap-2 border-r border-white/20 pr-4">
              <span className="size-2 bg-primary rounded-full shadow-[0_0_8px_rgba(54,226,123,1)]"></span>
              <span className="text-[10px] font-black uppercase tracking-widest text-white">
                DXF Processor Live
              </span>
            </div>
            <div className="flex items-center gap-5">
              <div className="flex flex-col">
                <span className="text-[8px] text-white/60 uppercase font-black tracking-widest">
                  Coord System
                </span>
                <span className="text-[11px] font-mono text-white font-bold">
                  UTM-32N / WGS84
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-[8px] text-white/60 uppercase font-black tracking-widest">
                  Layers Parsed
                </span>
                <span className="text-[11px] font-mono text-white font-bold">
                  42 / 42
                </span>
              </div>
            </div>
          </div>

          {/* Map Controls */}
          <div className="flex flex-col gap-2.5">
            <button className="glass-panel size-11 rounded-lg flex items-center justify-center text-white hover:text-primary hover:bg-white/10 transition-all shadow-xl">
              <Navigation className="w-5 h-5 font-bold" />
            </button>
            <div className="flex flex-col glass-panel rounded-lg overflow-hidden shadow-xl">
              <button className="size-11 flex items-center justify-center text-white hover:text-primary hover:bg-white/10 transition-all">
                <ZoomIn className="w-5 h-5 font-bold" />
              </button>
              <div className="h-px bg-white/20 mx-2"></div>
              <button className="size-11 flex items-center justify-center text-white hover:text-primary hover:bg-white/10 transition-all">
                <ZoomOut className="w-5 h-5 font-bold" />
              </button>
            </div>
            <button className="glass-panel size-11 rounded-lg flex items-center justify-center text-white hover:text-primary hover:bg-white/10 transition-all shadow-xl">
              <Layers className="w-5 h-5 font-bold" />
            </button>
          </div>
        </div>
      </main>
      {/* Floating Chat Button */}
      <FloatingChatButton projectId={params.id} />    </div>
  );
}
