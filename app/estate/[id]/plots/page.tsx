"use client";

import React, { useState, useEffect, use } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Plus, 
  Search,
  Filter,
  Download,
  MapPin,
  Copy,
  Loader2,
  FileSpreadsheet,
  FileText
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Plot {
  id: string;
  name: string;
  status: 'available' | 'sold' | 'reserved';
  area: number;
  price: number;
  location: string;
  buyer?: string;
  lastUpdated: string;
}

interface PlotsData {
  plots: Plot[];
  stats: {
    total: number;
    available: number;
    sold: number;
    reserved: number;
  };
}

export default function PlotsListPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [data, setData] = useState<PlotsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Export handler function
  const handleExport = async (format: 'csv' | 'pdf') => {
    if (!data || !data.plots || data.plots.length === 0) {
      alert('No plots to export');
      return;
    }

    setIsExporting(true);
    setExportError(null);

    try {
      const response = await fetch('/api/export/plots', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plots: data.plots,
          format: format,
        }),
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      // Create download link
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `plots_export_${new Date().toISOString().split('T')[0]}.${format === 'csv' ? 'csv' : 'txt'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      // Show success message
      alert(`Successfully exported ${data.plots.length} plots as ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Export error:', error);
      setExportError('Failed to export plots. Please try again.');
      alert('Failed to export plots. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  useEffect(() => {
    const fetchPlots = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `/api/plots/${id}?status=${statusFilter}&search=${searchTerm}`
        );
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Failed to fetch plots:', error);
      } finally {
        setIsLoading(false);
      }
    };

    const debounceTimer = setTimeout(() => {
      fetchPlots();
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [id, statusFilter, searchTerm]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-[#4CAF50] border-[#4CAF50]/40 text-white';
      case 'sold': return 'bg-[#9E9E9E] border-[#9E9E9E]/40 text-white';
      case 'reserved': return 'bg-[#FF9500] border-[#FF9500]/40 text-white';
      default: return 'bg-gray-500 border-gray-500/40 text-white';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#112117]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
          <p className="text-white/70">Loading plots...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#112117]">
        <p className="text-white/70">Failed to load plots</p>
      </div>
    );
  }

  const { plots, stats } = data;

  return (
    <div className="min-h-screen flex flex-col bg-[#112117]">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-[#366348] bg-[#122118] px-10 py-3">
        <div className="flex items-center gap-4 text-white">
          <div className="size-8 text-primary flex items-center justify-center">
            <MapPin className="w-8 h-8" />
          </div>
          <h2 className="text-white text-lg font-bold leading-tight tracking-[-0.015em]">
            DXF Parser
          </h2>
        </div>
        <div className="flex flex-1 justify-end gap-8">
          <nav className="hidden md:flex items-center gap-9">
            <Link href="/dashboard" className="text-white hover:text-primary transition-colors text-sm font-medium">
              Dashboard
            </Link>
            <Link href="/dashboard" className="text-primary text-sm font-medium">
              Estates
            </Link>
            <Link href="/settings" className="text-white hover:text-primary transition-colors text-sm font-medium">
              Settings
            </Link>
          </nav>
          <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border border-[#366348] bg-[#1b3224]" />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex justify-center py-5">
        <div className="flex flex-col w-full max-w-[1280px] px-4 md:px-10">
          
          {/* Breadcrumb */}
          <div className="flex flex-wrap gap-2 py-2">
            <Link href="/dashboard" className="text-[#95c6a9] hover:text-primary transition-colors text-xs font-medium">
              Home
            </Link>
            <span className="text-[#95c6a9] text-xs font-medium">/</span>
            <Link href="/dashboard" className="text-[#95c6a9] hover:text-primary transition-colors text-xs font-medium">
              Estates
            </Link>
            <span className="text-[#95c6a9] text-xs font-medium">/</span>
            <span className="text-white text-xs font-medium">Sunset Valley Estate</span>
          </div>

          {/* Page Header */}
          <div className="flex flex-wrap justify-between items-end gap-3 py-4 mb-2">
            <div className="flex flex-col gap-1">
              <h1 className="text-white text-3xl font-bold leading-tight tracking-tight">
                Sunset Valley Estate
              </h1>
              <p className="text-[#95c6a9] text-sm font-normal">
                Estate ID: #12345 • Last synced: Today, 10:23 AM
              </p>
            </div>
            <Button className="bg-primary hover:bg-[#2dc46b] transition-colors text-[#112117] text-sm font-bold shadow-[0_0_20px_rgba(54,226,123,0.2)]">
              <Plus className="w-5 h-5 mr-2" />
              Add Plot
            </Button>
          </div>

          {/* Tabs */}
          <div className="mb-6">
            <div className="flex border-b border-[#366348] gap-8">
              <Link href="/dashboard" className="border-b-2 border-transparent hover:border-[#366348] pb-3 pt-4 transition-all">
                <p className="text-[#95c6a9] hover:text-white text-sm font-semibold">Overview</p>
              </Link>
              <Link href={`/estate/${id}/map`} className="border-b-2 border-transparent hover:border-[#366348] pb-3 pt-4 transition-all">
                <p className="text-[#95c6a9] hover:text-white text-sm font-semibold">Technical Map</p>
              </Link>
              <div className="border-b-2 border-primary pb-3 pt-4">
                <p className="text-primary text-sm font-semibold">Plot Inventory</p>
              </div>
              <Link href="#" className="border-b-2 border-transparent hover:border-[#366348] pb-3 pt-4 transition-all">
                <p className="text-[#95c6a9] hover:text-white text-sm font-semibold">DXF Layers</p>
              </Link>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-[#1b3224] border border-[#366348] rounded-lg p-4">
              <p className="text-[#95c6a9] text-xs uppercase tracking-wider mb-2">Total Plots</p>
              <p className="text-white text-3xl font-bold">{stats.total}</p>
            </div>
            <div className="bg-[#1b3224] border border-[#366348] rounded-lg p-4">
              <p className="text-[#95c6a9] text-xs uppercase tracking-wider mb-2">Available</p>
              <p className="text-[#4CAF50] text-3xl font-bold">{stats.available}</p>
            </div>
            <div className="bg-[#1b3224] border border-[#366348] rounded-lg p-4">
              <p className="text-[#95c6a9] text-xs uppercase tracking-wider mb-2">Reserved</p>
              <p className="text-[#FF9500] text-3xl font-bold">{stats.reserved}</p>
            </div>
            <div className="bg-[#1b3224] border border-[#366348] rounded-lg p-4">
              <p className="text-[#95c6a9] text-xs uppercase tracking-wider mb-2">Sold</p>
              <p className="text-[#9E9E9E] text-3xl font-bold">{stats.sold}</p>
            </div>
          </div>

          {/* Filters and Search */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#95c6a9]" />
              <Input
                type="text"
                placeholder="Search by plot ID, name, or location..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-[#1b3224] border-[#366348] text-white placeholder:text-[#95c6a9]"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-[200px] bg-[#1b3224] border-[#366348] text-white">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent className="bg-[#1b3224] border-[#366348]">
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="available">Available</SelectItem>
                <SelectItem value="reserved">Reserved</SelectItem>
                <SelectItem value="sold">Sold</SelectItem>
              </SelectContent>
            </Select>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="outline" 
                  className="border-[#366348] text-white hover:bg-[#1b3224]"
                  disabled={isExporting}
                >
                  {isExporting ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4 mr-2" />
                  )}
                  Export
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="bg-[#1b3224] border-[#366348]">
                <DropdownMenuItem 
                  onClick={() => handleExport('csv')}
                  className="text-white hover:bg-[#0f1e15] hover:text-primary cursor-pointer"
                >
                  <FileSpreadsheet className="w-4 h-4 mr-2" />
                  Export as CSV
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => handleExport('pdf')}
                  className="text-white hover:bg-[#0f1e15] hover:text-primary cursor-pointer"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Export as PDF (Text)
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Data Table */}
          <div className="bg-[#1b3224] border border-[#366348] rounded-lg overflow-hidden">
            <Table>
              <TableHeader className="bg-[#112117]">
                <TableRow className="border-[#366348] hover:bg-[#112117]">
                  <TableHead className="text-[#95c6a9] font-bold">Plot ID</TableHead>
                  <TableHead className="text-[#95c6a9] font-bold">Name</TableHead>
                  <TableHead className="text-[#95c6a9] font-bold">Area (m²)</TableHead>
                  <TableHead className="text-[#95c6a9] font-bold">Price</TableHead>
                  <TableHead className="text-[#95c6a9] font-bold">Location</TableHead>
                  <TableHead className="text-[#95c6a9] font-bold">Status</TableHead>
                  <TableHead className="text-[#95c6a9] font-bold">Buyer/Reserved</TableHead>
                  <TableHead className="text-[#95c6a9] font-bold">Updated</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {plots.map((plot) => (
                  <TableRow 
                    key={plot.id} 
                    className="border-[#366348] hover:bg-[#122118] cursor-pointer transition-colors"
                  >
                    <TableCell className="font-mono text-white font-bold">
                      {plot.id}
                      <button className="ml-2 text-[#95c6a9] hover:text-primary transition-colors">
                        <Copy className="w-3 h-3" />
                      </button>
                    </TableCell>
                    <TableCell className="text-white font-medium">{plot.name}</TableCell>
                    <TableCell className="text-white">{plot.area.toFixed(1)}</TableCell>
                    <TableCell className="text-white font-medium">
                      ${plot.price.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-[#95c6a9]">{plot.location}</TableCell>
                    <TableCell>
                      <Badge className={`status-pill ${getStatusColor(plot.status)}`}>
                        {plot.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-[#95c6a9]">
                      {plot.buyer || '—'}
                    </TableCell>
                    <TableCell className="text-[#95c6a9] text-xs">
                      {plot.lastUpdated}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Results Summary */}
          <div className="mt-4 text-center text-[#95c6a9] text-sm">
            Showing {plots.length} of {stats.total} plots
          </div>
        </div>
      </div>
    </div>
  );
}
