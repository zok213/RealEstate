/**
 * Optimization Result Layer - Professional CAD-style rendering
 * Renders lots, parking spaces, green zones with tree patterns, and water features
 */
import React, { useEffect, useState } from 'react';
import { Polygon, SVGOverlay, useMap } from 'react-leaflet';
import L from 'leaflet';

interface Lot {
  geometry: {
    coordinates: number[][][];
  };
  properties: {
    lot_id: string;
    zone: string;
    area: number;
    frontage?: number;
    depth?: number;
  };
}

interface Amenity {
  type: string;
  geometry: {
    coordinates: number[][][];
  };
  properties?: {
    zone?: string;
    area?: number;
  };
}

interface OptimizationResult {
  lots: Lot[];
  amenities?: {
    parks?: Amenity[];
    lakes?: Amenity[];
    parking?: Amenity[];
  };
}

interface OptimizationResultLayerProps {
  result: OptimizationResult | null;
  showParking?: boolean;
  showTrees?: boolean;
}

// Zone color mapping - QCVN industrial zones
const ZONE_COLORS: { [key: string]: string } = {
  FACTORY: '#ef4444',      // Red - Industrial production
  WAREHOUSE: '#f59e0b',    // Orange - Logistics & storage
  SERVICE: '#06b6d4',      // Teal - Administrative & utilities
  RESIDENTIAL: '#fbbf24',  // Yellow (not in KCN per QCVN)
  GREEN: '#22c55e',        // Green - Parks & buffers
  WATER: '#3b82f6',        // Blue - Water features
};

const OptimizationResultLayer: React.FC<OptimizationResultLayerProps> = ({
  result,
  showParking = true,
  showTrees = true,
}) => {
  const map = useMap();
  const [bounds, setBounds] = useState<L.LatLngBounds | null>(null);

  useEffect(() => {
    if (!result || !result.lots || result.lots.length === 0) return;

    // Calculate bounds from all lots
    const allCoords: L.LatLngExpression[] = [];
    result.lots.forEach((lot) => {
      const coords = lot.geometry.coordinates[0];
      coords.forEach((coord) => {
        allCoords.push([coord[1], coord[0]] as L.LatLngExpression);
      });
    });

    if (allCoords.length > 0) {
      const latLngBounds = L.latLngBounds(allCoords);
      setBounds(latLngBounds);
      map.fitBounds(latLngBounds, { padding: [50, 50] });
    }
  }, [result, map]);

  if (!result) return null;

  // Convert GeoJSON coordinates [lng, lat] to Leaflet coordinates [lat, lng]
  const convertCoords = (coords: number[][]): [number, number][] => {
    return coords.map((coord) => [coord[1], coord[0]] as [number, number]);
  };

  // Generate parking pattern for a lot (small rectangles inside)
  const generateParkingPattern = (lot: Lot): JSX.Element[] => {
    if (!showParking) return [];

    const coords = lot.geometry.coordinates[0];
    const lotPolygon = L.polygon(convertCoords(coords));
    const lotBounds = lotPolygon.getBounds();
    const parkingSpots: JSX.Element[] = [];

    // Parking grid parameters (meters)
    const spotWidth = 2.5;  // 2.5m per spot
    const spotDepth = 5.0;  // 5m depth
    const rowSpacing = 6.0; // 6m between rows

    // Get lot dimensions
    const width = lotBounds.getEast() - lotBounds.getWest();
    const height = lotBounds.getNorth() - lotBounds.getSouth();

    // Calculate number of spots along frontage (15% of lot depth per QCVN)
    const parkingDepthRatio = 0.15;
    const numRows = Math.floor((height * parkingDepthRatio) / rowSpacing);
    const spotsPerRow = Math.floor(width / (spotWidth * 0.00001)); // Convert to degrees

    // Generate parking grid
    const startLat = lotBounds.getSouth();
    const startLng = lotBounds.getWest();

    for (let row = 0; row < Math.min(numRows, 2); row++) {
      for (let spot = 0; spot < Math.min(spotsPerRow, 8); spot++) {
        const lat = startLat + (row * rowSpacing * 0.00001);
        const lng = startLng + (spot * spotWidth * 0.00001);

        const spotCoords: [number, number][] = [
          [lat, lng],
          [lat, lng + spotWidth * 0.00001],
          [lat + spotDepth * 0.00001, lng + spotWidth * 0.00001],
          [lat + spotDepth * 0.00001, lng],
        ];

        parkingSpots.push(
          <Polygon
            key={`parking-${lot.properties.lot_id}-${row}-${spot}`}
            positions={spotCoords}
            pathOptions={{
              fillColor: '#64748b',
              fillOpacity: 0.3,
              color: '#475569',
              weight: 0.5,
              dashArray: '2, 2',
            }}
          />
        );
      }
    }

    return parkingSpots;
  };

  // Render tree pattern for green zones
  const renderTreePattern = (park: Amenity, index: number): JSX.Element | null => {
    if (!showTrees) return null;

    const coords = park.geometry.coordinates[0];
    const parkPolygon = L.polygon(convertCoords(coords));
    const parkBounds = parkPolygon.getBounds();
    const trees: JSX.Element[] = [];

    // Tree grid parameters
    const treeSpacing = 0.0001; // ~10m between trees
    const rows = Math.floor((parkBounds.getNorth() - parkBounds.getSouth()) / treeSpacing);
    const cols = Math.floor((parkBounds.getEast() - parkBounds.getWest()) / treeSpacing);

    // Limit tree count for performance
    for (let row = 0; row < Math.min(rows, 10); row++) {
      for (let col = 0; col < Math.min(cols, 10); col++) {
        const lat = parkBounds.getSouth() + row * treeSpacing;
        const lng = parkBounds.getWest() + col * treeSpacing;

        // Check if point is inside park polygon
        if (parkPolygon.getBounds().contains([lat, lng])) {
          trees.push(
            <circle
              key={`tree-${index}-${row}-${col}`}
              cx={lng}
              cy={lat}
              r={0.00002}
              fill="#22c55e"
              fillOpacity={0.6}
            />
          );
        }
      }
    }

    return bounds ? (
      <SVGOverlay key={`trees-${index}`} bounds={bounds}>
        <svg>
          <defs>
            <pattern
              id={`treePattern-${index}`}
              patternUnits="userSpaceOnUse"
              width="0.0002"
              height="0.0002"
            >
              <circle cx="0.0001" cy="0.0001" r="0.00003" fill="#22c55e" fillOpacity="0.7" />
            </pattern>
          </defs>
          {trees}
        </svg>
      </SVGOverlay>
    ) : null;
  };

  return (
    <>
      {/* LAYER 1: Green zones (parks, buffers) with tree pattern */}
      {result.amenities?.parks?.map((park, index) => (
        <React.Fragment key={`park-${index}`}>
          <Polygon
            positions={convertCoords(park.geometry.coordinates[0])}
            pathOptions={{
              fillColor: ZONE_COLORS.GREEN,
              fillOpacity: 0.4,
              color: '#16a34a',
              weight: 1.5,
              dashArray: '4, 4',
            }}
          />
          {renderTreePattern(park, index)}
        </React.Fragment>
      ))}

      {/* LAYER 2: Water features (lakes) */}
      {result.amenities?.lakes?.map((lake, index) => (
        <Polygon
          key={`lake-${index}`}
          positions={convertCoords(lake.geometry.coordinates[0])}
          pathOptions={{
            fillColor: ZONE_COLORS.WATER,
            fillOpacity: 0.5,
            color: '#2563eb',
            weight: 2,
          }}
        />
      ))}

      {/* LAYER 3: Lots with zone colors */}
      {result.lots.map((lot) => {
        const zone = lot.properties.zone || 'FACTORY';
        const fillColor = ZONE_COLORS[zone] || '#94a3b8';

        return (
          <React.Fragment key={lot.properties.lot_id}>
            <Polygon
              positions={convertCoords(lot.geometry.coordinates[0])}
              pathOptions={{
                fillColor: fillColor,
                fillOpacity: 0.5,
                color: '#1e293b',
                weight: 2,
              }}
              eventHandlers={{
                click: () => {
                  console.log('Lot clicked:', lot.properties);
                },
              }}
            >
              {/* Tooltip with lot info */}
              {/* <Tooltip permanent={false} direction="top">
                <div style={{ fontSize: '11px', fontWeight: 'bold' }}>
                  {lot.properties.lot_id}
                  <br />
                  {lot.properties.area.toFixed(0)}m²
                  <br />
                  {zone}
                </div>
              </Tooltip> */}
            </Polygon>

            {/* Parking spaces inside lot */}
            {generateParkingPattern(lot)}
          </React.Fragment>
        );
      })}

      {/* LAYER 4: Parking areas (dedicated parking zones) */}
      {showParking &&
        result.amenities?.parking?.map((parking, index) => (
          <Polygon
            key={`parking-area-${index}`}
            positions={convertCoords(parking.geometry.coordinates[0])}
            pathOptions={{
              fillColor: '#64748b',
              fillOpacity: 0.3,
              color: '#475569',
              weight: 1,
              dashArray: '3, 3',
            }}
          />
        ))}
    </>
  );
};

export default OptimizationResultLayer;
