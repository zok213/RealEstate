import { NextRequest, NextResponse } from 'next/server';

interface PlotData {
  id: string;
  name: string;
  area: number;
  price: number;
  location: string;
  status: string;
  zoning: string;
  buyer?: string;
  lastUpdated?: string;
}

// Convert plot data to CSV format
function convertToCSV(plots: PlotData[]): string {
  const headers = ['Plot ID', 'Name', 'Area (m²)', 'Price (USD)', 'Location', 'Status', 'Zoning', 'Buyer', 'Last Updated'];
  const csvRows = [headers.join(',')];

  plots.forEach(plot => {
    const row = [
      plot.id,
      `"${plot.name}"`,
      plot.area.toFixed(2),
      plot.price.toFixed(2),
      `"${plot.location}"`,
      plot.status,
      plot.zoning,
      plot.buyer || 'N/A',
      plot.lastUpdated || 'N/A'
    ];
    csvRows.push(row.join(','));
  });

  return csvRows.join('\n');
}

// Generate simple PDF (in real implementation, use a library like jsPDF or pdfkit)
function generatePDFContent(plots: PlotData[]): string {
  // This is a simplified version - in production, use a proper PDF library
  let content = 'INDUSTRIAL PARK PLOTS INVENTORY\n\n';
  content += `Generated: ${new Date().toLocaleString()}\n`;
  content += `Total Plots: ${plots.length}\n\n`;
  content += '='.repeat(80) + '\n\n';

  plots.forEach((plot, index) => {
    content += `${index + 1}. ${plot.name} (${plot.id})\n`;
    content += `   Area: ${plot.area} m²\n`;
    content += `   Price: $${plot.price.toLocaleString()}\n`;
    content += `   Location: ${plot.location}\n`;
    content += `   Status: ${plot.status.toUpperCase()}\n`;
    content += `   Zoning: ${plot.zoning}\n`;
    if (plot.buyer) {
      content += `   Buyer: ${plot.buyer}\n`;
    }
    content += '\n';
  });

  return content;
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { plots, format } = body;

    if (!plots || !Array.isArray(plots)) {
      return NextResponse.json(
        { error: 'Invalid plot data' },
        { status: 400 }
      );
    }

    if (!format || !['csv', 'pdf'].includes(format)) {
      return NextResponse.json(
        { error: 'Invalid format. Must be "csv" or "pdf"' },
        { status: 400 }
      );
    }

    if (format === 'csv') {
      const csv = convertToCSV(plots);
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `industrial_park_plots_${timestamp}.csv`;

      return new Response(csv, {
        status: 200,
        headers: {
          'Content-Type': 'text/csv',
          'Content-Disposition': `attachment; filename="${filename}"`,
        },
      });
    } else if (format === 'pdf') {
      // For now, return as plain text. In production, use a PDF library
      const pdfContent = generatePDFContent(plots);
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `industrial_park_plots_${timestamp}.txt`;

      return new Response(pdfContent, {
        status: 200,
        headers: {
          'Content-Type': 'text/plain',
          'Content-Disposition': `attachment; filename="${filename}"`,
        },
      });
    }

    return NextResponse.json({ error: 'Unknown error' }, { status: 500 });
  } catch (error) {
    console.error('Export error:', error);
    return NextResponse.json(
      { error: 'Failed to generate export' },
      { status: 500 }
    );
  }
}
