import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8001";

interface PlotDetail {
  id: string;
  name: string;
  status: 'available' | 'sold' | 'reserved';
  area: number;
  price: number;
  pricePerSqm: number;
  location: string;
  coordinates: string;
  zoning: string;
  buyer?: string;
  lastUpdated: string;
  details: {
    buildingCoverage: number;
    maxHeight: string;
    utilities: string[];
    accessRoad: string;
    soilType: string;
  };
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string; plotId: string }> }
) {
  try {
    const { id, plotId } = await params;

    // Try to fetch from backend
    const response = await fetch(
      `${BACKEND_URL}/api/projects/${id}/plots/${plotId}`,
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
    const mockPlotData: Record<string, PlotDetail> = {
      'P-001': {
        id: 'P-001',
        name: 'Plot A1',
        status: 'available',
        area: 450.5,
        price: 225000,
        pricePerSqm: 500,
        location: 'North Section',
        coordinates: '10.762622, 106.660172',
        zoning: 'IND-1',
        lastUpdated: '2 days ago',
        details: {
          buildingCoverage: 60,
          maxHeight: '12m (3 floors)',
          utilities: ['Water', 'Electricity', 'Sewage', 'Internet'],
          accessRoad: 'Main Road A - 12m wide',
          soilType: 'Clay loam, suitable for industrial construction'
        }
      },
      'P-042': {
        id: 'P-042',
        name: 'Plot D5',
        status: 'available',
        area: 540.00,
        price: 125000,
        pricePerSqm: 231.48,
        location: 'West Section - Premium Location',
        coordinates: '37.38, -122.03',
        zoning: 'R-2-ENG',
        lastUpdated: '3 hours ago',
        details: {
          buildingCoverage: 65,
          maxHeight: '15m (4 floors)',
          utilities: ['Water', 'Electricity', 'Sewage', 'Fiber Optic', 'Gas'],
          accessRoad: 'Highway Access - 20m wide',
          soilType: 'Sandy clay, excellent load-bearing capacity'
        }
      },
      'P-003': {
        id: 'P-003',
        name: 'Plot B1',
        status: 'reserved',
        area: 380.2,
        price: 190000,
        pricePerSqm: 500,
        location: 'East Section',
        coordinates: '10.763022, 106.660572',
        zoning: 'IND-2',
        buyer: 'Tech Industries Co.',
        lastUpdated: '3 days ago',
        details: {
          buildingCoverage: 55,
          maxHeight: '10m (2 floors)',
          utilities: ['Water', 'Electricity', 'Sewage'],
          accessRoad: 'Service Road B - 8m wide',
          soilType: 'Mixed soil with good drainage'
        }
      }
    };

    const plotData = mockPlotData[plotId] || mockPlotData['P-042'];

    return NextResponse.json(plotData);

  } catch (error) {
    console.error('Plot detail API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch plot details' },
      { status: 500 }
    );
  }
}
