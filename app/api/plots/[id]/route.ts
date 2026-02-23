import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8001";

interface Plot {
  id: string;
  name: string;
  status: 'available' | 'sold' | 'reserved';
  area: number;
  price: number;
  location: string;
  buyer?: string;
  lastUpdated: string;
  zoning?: string;
  coordinates?: string;
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const { searchParams } = new URL(req.url);
    const status = searchParams.get('status');
    const search = searchParams.get('search');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');

    // Try to fetch from backend
    const response = await fetch(
      `${BACKEND_URL}/api/projects/${id}/plots?status=${status || 'all'}&search=${search || ''}&page=${page}&limit=${limit}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      }
    );

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    }

    // Return mock data if backend fails
    const mockPlots: Plot[] = [
      { id: 'P-001', name: 'Plot A1', status: 'available', area: 450.5, price: 225000, location: 'North Section', lastUpdated: '2 days ago', zoning: 'IND-1', coordinates: '10.762622, 106.660172' },
      { id: 'P-002', name: 'Plot A2', status: 'sold', area: 520.0, price: 260000, location: 'North Section', buyer: 'ABC Corp', lastUpdated: '1 week ago', zoning: 'IND-1', coordinates: '10.762822, 106.660372' },
      { id: 'P-003', name: 'Plot B1', status: 'reserved', area: 380.2, price: 190000, location: 'East Section', buyer: 'Tech Industries', lastUpdated: '3 days ago', zoning: 'IND-2', coordinates: '10.763022, 106.660572' },
      { id: 'P-004', name: 'Plot B2', status: 'available', area: 495.8, price: 247900, location: 'East Section', lastUpdated: '1 day ago', zoning: 'IND-2', coordinates: '10.763222, 106.660772' },
      { id: 'P-005', name: 'Plot C1', status: 'available', area: 540.0, price: 270000, location: 'South Section', lastUpdated: '5 hours ago', zoning: 'IND-1', coordinates: '10.763422, 106.660972' },
      { id: 'P-006', name: 'Plot C2', status: 'sold', area: 425.5, price: 212750, location: 'South Section', buyer: 'XYZ Ltd', lastUpdated: '2 weeks ago', zoning: 'IND-1', coordinates: '10.763622, 106.661172' },
      { id: 'P-007', name: 'Plot D1', status: 'available', area: 510.3, price: 255150, location: 'West Section', lastUpdated: '1 day ago', zoning: 'IND-2', coordinates: '10.763822, 106.661372' },
      { id: 'P-008', name: 'Plot D2', status: 'reserved', area: 470.0, price: 235000, location: 'West Section', buyer: 'Global Inc', lastUpdated: '4 days ago', zoning: 'IND-2', coordinates: '10.764022, 106.661572' },
      { id: 'P-009', name: 'Plot E1', status: 'available', area: 415.0, price: 207500, location: 'North Section', lastUpdated: '6 hours ago', zoning: 'IND-1', coordinates: '10.764222, 106.661772' },
      { id: 'P-010', name: 'Plot E2', status: 'available', area: 485.5, price: 242750, location: 'East Section', lastUpdated: '12 hours ago', zoning: 'IND-2', coordinates: '10.764422, 106.661972' },
      { id: 'P-011', name: 'Plot F1', status: 'sold', area: 530.0, price: 265000, location: 'South Section', buyer: 'Manufacturing Co', lastUpdated: '3 weeks ago', zoning: 'IND-1', coordinates: '10.764622, 106.662172' },
      { id: 'P-012', name: 'Plot F2', status: 'reserved', area: 395.0, price: 197500, location: 'West Section', buyer: 'Logistics Ltd', lastUpdated: '1 week ago', zoning: 'IND-2', coordinates: '10.764822, 106.662372' },
    ];

    // Apply filters
    let filteredPlots = mockPlots;
    
    if (status && status !== 'all') {
      filteredPlots = filteredPlots.filter(plot => plot.status === status);
    }

    if (search) {
      const searchLower = search.toLowerCase();
      filteredPlots = filteredPlots.filter(plot =>
        plot.id.toLowerCase().includes(searchLower) ||
        plot.name.toLowerCase().includes(searchLower) ||
        plot.location.toLowerCase().includes(searchLower)
      );
    }

    // Calculate stats
    const stats = {
      total: mockPlots.length,
      available: mockPlots.filter(p => p.status === 'available').length,
      sold: mockPlots.filter(p => p.status === 'sold').length,
      reserved: mockPlots.filter(p => p.status === 'reserved').length,
    };

    return NextResponse.json({
      plots: filteredPlots,
      stats,
      pagination: {
        page,
        limit,
        total: filteredPlots.length,
        totalPages: Math.ceil(filteredPlots.length / limit)
      }
    });

  } catch (error) {
    console.error('Plots API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch plots' },
      { status: 500 }
    );
  }
}
