/**
 * Professional Map View Demo
 * Displays optimization results with CAD-style rendering
 */
import React, { useState, useEffect } from 'react';
import MapView from './components/MapView/MapView';
import { apiService } from './services/api';
import { Loader2, Eye, EyeOff } from 'lucide-react';
import './styles/design-system.css';

function ProfessionalMapDemo() {
  const [optimizationResult, setOptimizationResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showParking, setShowParking] = useState(true);
  const [showTrees, setShowTrees] = useState(true);

  // Load optimization result
  const loadOptimizationResult = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.getOptimizationResult();
      console.log('📊 Optimization result loaded:', result);
      setOptimizationResult(result);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load optimization result';
      setError(errorMsg);
      console.error('❌ Error loading optimization:', err);
    } finally {
      setLoading(false);
    }
  };

  // Auto-load on mount
  useEffect(() => {
    loadOptimizationResult();
  }, []);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <Loader2 size={48} className="spin" style={{ color: '#3b82f6' }} />
        <p style={{ fontSize: '18px', color: '#64748b' }}>Loading optimization result...</p>
      </div>
    );
  }

  if (error && !optimizationResult) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '16px',
        padding: '32px'
      }}>
        <div style={{
          background: '#fef2f2',
          border: '1px solid #fca5a5',
          borderRadius: '12px',
          padding: '24px',
          maxWidth: '600px'
        }}>
          <h2 style={{ color: '#dc2626', marginBottom: '12px' }}>⚠️ No Optimization Result</h2>
          <p style={{ color: '#991b1b', marginBottom: '16px' }}>{error}</p>
          <p style={{ color: '#64748b', fontSize: '14px', marginBottom: '16px' }}>
            Please run an optimization first by:
          </p>
          <ol style={{ color: '#475569', fontSize: '14px', paddingLeft: '24px' }}>
            <li>Go to <a href="http://127.0.0.1:8000/static/index.html" target="_blank" rel="noopener noreferrer" style={{ color: '#3b82f6' }}>http://127.0.0.1:8000/static/index.html</a></li>
            <li>Upload a DXF boundary file</li>
            <li>Click "Optimize Layout"</li>
            <li>Return to this page</li>
          </ol>
          <button
            onClick={loadOptimizationResult}
            style={{
              marginTop: '16px',
              padding: '12px 24px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            🔄 Try Again
          </button>
        </div>
      </div>
    );
  }

  // Extract boundary from first lot if available
  const boundary: [number, number][] | undefined = optimizationResult?.lots?.[0]?.geometry?.coordinates?.[0]?.map(
    (coord: number[]) => [coord[1], coord[0]] as [number, number]
  );

  const centerCoords: [number, number] | undefined = boundary
    ? [
        (Math.min(...boundary.map(b => b[0])) + Math.max(...boundary.map(b => b[0]))) / 2,
        (Math.min(...boundary.map(b => b[1])) + Math.max(...boundary.map(b => b[1]))) / 2,
      ]
    : undefined;

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Control Panel */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: '700', color: '#1e293b', margin: 0 }}>
            🏭 Professional CAD-Style Map View
          </h1>
          <p style={{ fontSize: '13px', color: '#64748b', margin: '4px 0 0 0' }}>
            QCVN 01:2021/BXD Industrial Zone Design
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button
            onClick={() => setShowParking(!showParking)}
            style={{
              padding: '8px 16px',
              background: showParking ? '#3b82f6' : '#e5e7eb',
              color: showParking ? 'white' : '#475569',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            {showParking ? <Eye size={16} /> : <EyeOff size={16} />}
            Parking Spaces
          </button>
          
          <button
            onClick={() => setShowTrees(!showTrees)}
            style={{
              padding: '8px 16px',
              background: showTrees ? '#22c55e' : '#e5e7eb',
              color: showTrees ? 'white' : '#475569',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            {showTrees ? <Eye size={16} /> : <EyeOff size={16} />}
            Tree Pattern
          </button>

          <button
            onClick={loadOptimizationResult}
            style={{
              padding: '8px 16px',
              background: '#f59e0b',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '600'
            }}
          >
            🔄 Reload
          </button>
        </div>
      </div>

      {/* Statistics */}
      {optimizationResult?.statistics && (
        <div style={{
          background: '#f8fafc',
          borderBottom: '1px solid #e5e7eb',
          padding: '12px 24px',
          display: 'flex',
          gap: '24px',
          fontSize: '13px'
        }}>
          <div style={{ display: 'flex', gap: '6px' }}>
            <span style={{ color: '#64748b', fontWeight: '600' }}>Lots:</span>
            <span style={{ color: '#1e293b' }}>{optimizationResult.statistics.total_lots || 0}</span>
          </div>
          <div style={{ display: 'flex', gap: '6px' }}>
            <span style={{ color: '#64748b', fontWeight: '600' }}>Parks:</span>
            <span style={{ color: '#1e293b' }}>{optimizationResult.statistics.total_parks || 0}</span>
          </div>
          <div style={{ display: 'flex', gap: '6px' }}>
            <span style={{ color: '#64748b', fontWeight: '600' }}>Parking Areas:</span>
            <span style={{ color: '#1e293b' }}>{optimizationResult.amenities?.parking?.length || 0}</span>
          </div>
          <div style={{ display: 'flex', gap: '6px' }}>
            <span style={{ color: '#64748b', fontWeight: '600' }}>Water Features:</span>
            <span style={{ color: '#1e293b' }}>{optimizationResult.amenities?.lakes?.length || 0}</span>
          </div>
        </div>
      )}

      {/* Map View */}
      <div style={{ flex: 1 }}>
        <MapView
          estateId="professional-demo"
          boundary={boundary}
          centerCoords={centerCoords}
          designMode={false}
          optimizationResult={optimizationResult}
          showParking={showParking}
          showTrees={showTrees}
        />
      </div>
    </div>
  );
}

export default ProfessionalMapDemo;
