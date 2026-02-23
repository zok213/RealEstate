import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8001";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const projectId = searchParams.get('projectId') || 'default';

    // Fetch project stats from backend
    const response = await fetch(`${BACKEND_URL}/api/projects/${projectId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      // Return mock data if backend fails
      return NextResponse.json({
        project: {
          id: projectId,
          name: "KCN Tiên Sơn",
          location: "Bắc Ninh, Vietnam",
          total_area: 2540,
          total_plots: 47,
          estimated_value: 15800000,
          last_updated: new Date().toISOString()
        },
        stats: {
          available_plots: 28,
          reserved_plots: 12,
          sold_plots: 7
        },
        recent_activity: [
          {
            id: '1',
            action: 'DXF File Uploaded',
            description: 'kcn_song_than_binh_duong.dxf processed successfully',
            timestamp: '2 hours ago',
            status: 'completed'
          },
          {
            id: '2',
            action: 'Layout Generated',
            description: '47 plots optimized for industrial use',
            timestamp: '3 hours ago',
            status: 'completed'
          },
          {
            id: '3',
            action: 'Compliance Check',
            description: 'IEAT standards validation in progress',
            timestamp: '5 hours ago',
            status: 'processing'
          },
          {
            id: '4',
            action: 'Plot P-042 Reserved',
            description: 'Client reserved 540 m² plot',
            timestamp: '1 day ago',
            status: 'completed'
          }
        ]
      });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Dashboard API error:', error);
    
    // Return mock data on error
    return NextResponse.json({
      project: {
        id: 'default',
        name: "KCN Tiên Sơn",
        location: "Bắc Ninh, Vietnam",
        total_area: 2540,
        total_plots: 47,
        estimated_value: 15800000,
        last_updated: new Date().toISOString()
      },
      stats: {
        available_plots: 28,
        reserved_plots: 12,
        sold_plots: 7
      },
      recent_activity: []
    });
  }
}
