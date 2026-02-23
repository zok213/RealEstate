import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polygon, Polyline, Marker, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import { useDesignStore } from '../../store/designStore';
import { DesignElement } from '../../types';
import DesignToolbar from './DesignToolbar';
import PropertiesEditor from './PropertiesEditor';
import ChatbotPanel from './ChatbotPanel';
import OptimizationResultLayer from './OptimizationResultLayer';
import './MapView.css';

interface MapViewProps {
  estateId: string;
  boundary?: [number, number][];
  centerCoords?: [number, number];
  designMode?: boolean;
  onToggleDesignMode?: () => void;
  optimizationResult?: any; // Optimization result from backend API
  showParking?: boolean;
  showTrees?: boolean;
}

// Fix Leaflet default icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapView: React.FC<MapViewProps> = ({
  estateId,
  boundary,
  centerCoords,
  designMode = false,
  onToggleDesignMode,
  optimizationResult = null,
  showParking = true,
  showTrees = true,
}) => {
  const [center, setCenter] = useState<[number, number]>(
    centerCoords || [21.0285, 105.8542]
  );
  const [zoom, setZoom] = useState(15);
  const mapRef = useRef<L.Map | null>(null);

  const {
    elements,
    currentTool,
    selectedElement,
    layers,
    snapToGrid,
  } = useDesignStore();

  useEffect(() => {
    if (boundary && boundary.length > 0) {
      // Calculate center from boundary
      const lats = boundary.map((coord) => coord[0]);
      const lngs = boundary.map((coord) => coord[1]);
      const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
      const centerLng = (Math.min(...lngs) + Math.max(...lngs)) / 2;
      setCenter([centerLat, centerLng]);
    }
  }, [boundary]);

  const renderElements = () => {
    return elements.map((element) => {
      if (!layers[element.type as keyof typeof layers]) {
        return null;
      }

      switch (element.type) {
        case 'road':
          return (
            <Polyline
              key={element.id}
              positions={element.geometry.coordinates as any}
              pathOptions={{
                color: element.style?.color || '#ffffff',
                weight: element.properties.width || 25,
                opacity: element.style?.opacity || 1,
              }}
            />
          );

        case 'building':
          return (
            <Polygon
              key={element.id}
              positions={element.geometry.coordinates as any}
              pathOptions={{
                fillColor: element.style?.fillColor || '#94a3b8',
                fillOpacity: 0.7,
                color: '#475569',
                weight: 2,
              }}
            />
          );

        case 'plot':
          return (
            <Polygon
              key={element.id}
              positions={element.geometry.coordinates as any}
              pathOptions={{
                fillColor: element.style?.fillColor || '#10b981',
                fillOpacity: 0.3,
                color: '#059669',
                weight: 2,
              }}
            />
          );

        default:
          return null;
      }
    });
  };

  return (
    <div className="map-view-container">
      {/* Header */}
      <div className="map-header">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-semibold">Map View - Estate {estateId}</h2>
          {designMode && <span className="badge badge-info">✏️ Design Mode</span>}
        </div>
        <div className="flex items-center gap-2">
          <button
            className={`btn ${designMode ? 'btn-secondary' : 'btn-primary'}`}
            onClick={onToggleDesignMode}
          >
            {designMode ? '← Exit Design Mode' : '✏️ Design Mode'}
          </button>
          <button className="btn btn-secondary">
            📥 Export
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="map-content">
        {designMode && (
          <div className="design-sidebar">
            <DesignToolbar />
            <PropertiesEditor />
          </div>
        )}

        <div className="map-container-wrapper">
          <MapContainer
            center={center}
            zoom={zoom}
            style={{ height: '100%', width: '100%' }}
            ref={mapRef as any}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />

            {/* Estate Boundary */}
            {boundary && boundary.length > 0 && (
              <Polygon
                positions={boundary}
                pathOptions={{
                  color: '#3b82f6',
                  weight: 3,
                  fillColor: '#3b82f6',
                  fillOpacity: 0.1,
                }}
              />
            )}

            {/* Design Elements */}
            {renderElements()}

            {/* Optimization Results - Professional CAD Style */}
            {optimizationResult && (
              <OptimizationResultLayer
                result={optimizationResult}
                showParking={showParking}
                showTrees={showTrees}
              />
            )}

            {/* Grid Overlay (when snap to grid is enabled) */}
            {designMode && snapToGrid && (
              <div className="grid-overlay">
                {/* Grid lines will be rendered here */}
              </div>
            )}
          </MapContainer>

          {/* Legend */}
          <div className="map-legend">
            <h3 className="font-semibold mb-3">📍 Layers</h3>
            
            {optimizationResult && (
              <>
                <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '8px', color: '#64748b' }}>
                  ZONE TYPES (QCVN)
                </div>
                <div className="map-legend-item">
                  <div className="map-legend-color" style={{ background: '#ef4444' }} />
                  <span>Factory (Sản xuất)</span>
                </div>
                <div className="map-legend-item">
                  <div className="map-legend-color" style={{ background: '#f59e0b' }} />
                  <span>Warehouse (Kho)</span>
                </div>
                <div className="map-legend-item">
                  <div className="map-legend-color" style={{ background: '#06b6d4' }} />
                  <span>Service (Dịch vụ)</span>
                </div>
                <div className="map-legend-item">
                  <div className="map-legend-color" style={{ background: '#22c55e' }} />
                  <span>Green/Parks (Cây xanh)</span>
                </div>
                <div className="map-legend-item">
                  <div className="map-legend-color" style={{ background: '#3b82f6' }} />
                  <span>Water (Mặt nước)</span>
                </div>
                <div className="map-legend-item">
                  <div className="map-legend-color" style={{ background: '#64748b', border: '1px dashed #475569' }} />
                  <span>Parking (Bãi đỗ xe)</span>
                </div>
                
                <div style={{ borderTop: '1px solid #e5e7eb', margin: '12px 0', paddingTop: '12px' }}>
                  <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '8px', color: '#64748b' }}>
                    DISPLAY OPTIONS
                  </div>
                  <div className="map-legend-item">
                    <input type="checkbox" checked={showParking} readOnly />
                    <span>Parking Spaces</span>
                  </div>
                  <div className="map-legend-item">
                    <input type="checkbox" checked={showTrees} readOnly />
                    <span>Tree Pattern</span>
                  </div>
                </div>
              </>
            )}
            
            {!optimizationResult && (
              <>
                <div className="map-legend-item">
                  <input type="checkbox" checked={layers.plots} readOnly />
                  <div className="map-legend-color" style={{ background: '#10b981' }} />
                  <span>Plots</span>
                </div>
                <div className="map-legend-item">
                  <input type="checkbox" checked={layers.roads} readOnly />
                  <div className="map-legend-color" style={{ background: '#ffffff', border: '2px solid #000' }} />
                  <span>Roads</span>
                </div>
                <div className="map-legend-item">
                  <input type="checkbox" checked={layers.buildings} readOnly />
                  <div className="map-legend-color" style={{ background: '#94a3b8' }} />
                  <span>Buildings</span>
                </div>
                <div className="map-legend-item">
                  <input type="checkbox" checked={layers.utilities} readOnly />
                  <div className="map-legend-color" style={{ background: '#f59e0b' }} />
                  <span>Utilities</span>
                </div>
                <div className="map-legend-item">
                  <input type="checkbox" checked={layers.greenAreas} readOnly />
                  <div className="map-legend-color" style={{ background: '#22c55e' }} />
                  <span>Green Areas</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Chatbot Panel (only in design mode) */}
      {designMode && <ChatbotPanel estateId={estateId} />}
    </div>
  );
};

export default MapView;
