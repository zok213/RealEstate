"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import Map, { Source, Layer } from "react-map-gl"
import type { MapRef } from "react-map-gl"
import type { IndustrialParkLayout } from "@/types/industrial-park"
import { useDesign } from "@/contexts/design-context"
import "mapbox-gl/dist/mapbox-gl.css"

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN

interface MapboxCanvasProps {
    zoom: number
    layout?: IndustrialParkLayout | null
    visibleLayers: {
        roads: boolean
        buildings: boolean
        greenSpace: boolean
        parking: boolean
        utilities: boolean
        fireProtection: boolean
    }
    mapStyle?: "satellite" | "streets" | "light" | "dark"
}

// Color constants
const COLORS = {
    roads: {
        primary: "#607D8B",
        secondary: "#78909C",
        industrial: "#90A4AE",
        service: "#B0BEC5",
        fire: "#EF5350",
    },
    buildings: {
        manufacturing: "#E53935",
        warehouse: "#FB8C00",
        office: "#8E24AA",
        utility: "#FBC02D",
    },
    greenSpace: "#4CAF50",
    parking: {
        car: "#9E9E9E",
        truck: "#757575",
    },
    utilities: {
        power: "#FF6F00",
        water: "#1976D2",
        waste: "#43A047",
    },
    fire: "#D32F2F",
}

// Map style URLs
const MAP_STYLES = {
    satellite: "mapbox://styles/mapbox/satellite-streets-v12",
    streets: "mapbox://styles/mapbox/streets-v12",
    light: "mapbox://styles/mapbox/light-v11",
    dark: "mapbox://styles/mapbox/dark-v11",
}

export function MapboxCanvas({
    zoom,
    layout,
    visibleLayers,
    mapStyle = "satellite"
}: MapboxCanvasProps) {
    const mapRef = useRef<MapRef>(null)
    const containerRef = useRef<HTMLDivElement>(null)
    const { siteBoundary, siteInfo } = useDesign()

    const [viewState, setViewState] = useState({
        latitude: 21.053,
        longitude: 105.725,
        zoom: zoom,
        pitch: 45,
        bearing: 0,
    })
    const [hoveredItem, setHoveredItem] = useState<{
        type: string
        name: string
        x: number
        y: number
        details?: string
    } | null>(null)

    // ResizeObserver to handle container size changes (sidebar collapse/expand)
    useEffect(() => {
        const container = containerRef.current
        if (!container) return

        const resizeObserver = new ResizeObserver(() => {
            // Trigger map resize after a small delay to allow CSS transitions
            setTimeout(() => {
                if (mapRef.current) {
                    mapRef.current.resize()
                }
            }, 100)
        })

        resizeObserver.observe(container)

        return () => {
            resizeObserver.disconnect()
        }
    }, [])

    // Update view when site boundary is loaded
    useEffect(() => {
        if (siteInfo?.center) {
            setViewState(prev => ({
                ...prev,
                latitude: siteInfo.center.latitude,
                longitude: siteInfo.center.longitude,
                zoom: 14,
            }))
        }
    }, [siteInfo])

    // Convert layout data to GeoJSON
    const layoutToGeoJSON = useCallback(() => {
        if (!layout) return null

        const features: any[] = []

        // Helper to safely map coordinates
        const safeMapCoords = (coords: any[] | undefined | null) => {
            if (!Array.isArray(coords)) return []
            return coords.map(c => [c?.longitude || 0, c?.latitude || 0])
        }

        // Green spaces polygons
        const greenSpaces = Array.isArray(layout.greenSpaces) ? layout.greenSpaces : []
        if (visibleLayers.greenSpace && greenSpaces.length > 0) {
            greenSpaces.forEach((space, idx) => {
                if (!space) return // Skip null/undefined entries
                const coords = Array.isArray(space.coordinates) ? space.coordinates : []
                if (coords.length < 3) return // Skip if not enough points for polygon

                const mappedCoords = safeMapCoords(coords)
                if (mappedCoords.length < 3) return

                const polygonCoords = [...mappedCoords, mappedCoords[0]] // Close the polygon

                features.push({
                    type: "Feature",
                    id: `green-${idx}`,
                    geometry: {
                        type: "Polygon",
                        coordinates: [polygonCoords]
                    },
                    properties: {
                        layer: "greenSpace",
                        area: space.area || 0,
                        trees: space.trees || 0,
                        type: space.type || "park",
                    }
                })
            })
        }

        // Roads as lines
        const roads = Array.isArray(layout.roads) ? layout.roads : []
        if (visibleLayers.roads && roads.length > 0) {
            roads.forEach((road, idx) => {
                if (!road) return // Skip null/undefined entries
                const coords = Array.isArray(road.coordinates) ? road.coordinates : []
                if (coords.length < 2) return // Skip if not enough points for line

                const mappedCoords = safeMapCoords(coords)
                if (mappedCoords.length < 2) return

                features.push({
                    type: "Feature",
                    id: `road-${idx}`,
                    geometry: {
                        type: "LineString",
                        coordinates: mappedCoords
                    },
                    properties: {
                        layer: "roads",
                        name: road.name || '',
                        type: road.type || 'secondary',
                        width: road.width || 8,
                        color: COLORS.roads[road.type as keyof typeof COLORS.roads] || "#607D8B",
                    }
                })
            })
        }

        // Buildings as polygons
        const buildings = Array.isArray(layout.buildings) ? layout.buildings : []
        if (visibleLayers.buildings && buildings.length > 0) {
            buildings.forEach((building, idx) => {
                if (!building) return // Skip null/undefined entries
                const size = Array.isArray(building.size) ? building.size : [50, 50]
                const [w, h] = [size[0] || 50, size[1] || 50]
                const lon = building.coordinates?.longitude || 0
                const lat = building.coordinates?.latitude || 0
                if (!lon || !lat) return // Skip if no coordinates
                // Approximate building polygon (rectangle)
                const halfW = w * 0.000005 // Convert to approx degrees
                const halfH = h * 0.000005

                features.push({
                    type: "Feature",
                    id: `building-${idx}`,
                    geometry: {
                        type: "Polygon",
                        coordinates: [[
                            [lon - halfW, lat - halfH],
                            [lon + halfW, lat - halfH],
                            [lon + halfW, lat + halfH],
                            [lon - halfW, lat + halfH],
                            [lon - halfW, lat - halfH],
                        ]]
                    },
                    properties: {
                        layer: "buildings",
                        name: building.name || '',
                        type: building.type || 'manufacturing',
                        floors: building.floors || 1,
                        color: COLORS.buildings[building.type as keyof typeof COLORS.buildings] || "#E53935",
                        height: (building.floors || 1) * 4, // 4m per floor for 3D
                    }
                })
            })
        }

        // Parking as rectangles
        const parkingLots = Array.isArray(layout.parking) ? layout.parking : []
        if (visibleLayers.parking && parkingLots.length > 0) {
            parkingLots.forEach((parking, idx) => {
                if (!parking) return // Skip null/undefined entries
                const lon = parking.coordinates?.longitude || 0
                const lat = parking.coordinates?.latitude || 0
                if (!lon || !lat) return // Skip if no coordinates
                const size = parking.type === "truck" ? 0.0003 : 0.00025

                features.push({
                    type: "Feature",
                    id: `parking-${idx}`,
                    geometry: {
                        type: "Polygon",
                        coordinates: [[
                            [lon - size, lat - size],
                            [lon + size, lat - size],
                            [lon + size, lat + size],
                            [lon - size, lat + size],
                            [lon - size, lat - size],
                        ]]
                    },
                    properties: {
                        layer: "parking",
                        type: parking.type || 'car',
                        spaces: parking.spaces || 0,
                        color: COLORS.parking[parking.type as keyof typeof COLORS.parking] || "#9E9E9E",
                    }
                })
            })
        }

        // Utilities as points
        const utilities = Array.isArray(layout.utilities) ? layout.utilities : []
        if (visibleLayers.utilities && utilities.length > 0) {
            utilities.forEach((utility, idx) => {
                if (!utility) return // Skip null/undefined entries
                const lon = utility.coordinates?.longitude
                const lat = utility.coordinates?.latitude
                if (!lon || !lat) return // Skip if no coordinates

                features.push({
                    type: "Feature",
                    id: `utility-${idx}`,
                    geometry: {
                        type: "Point",
                        coordinates: [lon, lat]
                    },
                    properties: {
                        layer: "utilities",
                        name: utility.label || utility.type || 'Utility',
                        type: utility.type || 'unknown',
                        capacity: utility.capacity || 'N/A',
                        icon: utility.type?.includes("power") ? "⚡" :
                            utility.type?.includes("water") ? "💧" : "♻",
                    }
                })
            })
        }

        // Fire protection as points
        const fireProtection = Array.isArray(layout.fireProtection) ? layout.fireProtection : []
        if (visibleLayers.fireProtection && fireProtection.length > 0) {
            fireProtection.forEach((item, idx) => {
                if (!item) return // Skip null/undefined entries
                const lon = item.coordinates?.longitude
                const lat = item.coordinates?.latitude
                if (!lon || !lat) return // Skip if no coordinates

                features.push({
                    type: "Feature",
                    id: `fire-${idx}`,
                    geometry: {
                        type: "Point",
                        coordinates: [lon, lat]
                    },
                    properties: {
                        layer: "fireProtection",
                        type: item.type || 'hydrant',
                        name: item.label || `PCCC ${idx + 1}`,
                    }
                })
            })
        }

        return {
            type: "FeatureCollection",
            features
        }
    }, [layout, visibleLayers])

    const geoJSON = layoutToGeoJSON()

    if (!MAPBOX_TOKEN) {
        return (
            <div className="absolute inset-0 flex items-center justify-center bg-muted">
                <div className="text-center p-4">
                    <p className="text-destructive font-semibold">Mapbox Token không tìm thấy</p>
                    <p className="text-sm text-muted-foreground mt-2">
                        Vui lòng thêm NEXT_PUBLIC_MAPBOX_TOKEN vào file .env.local
                    </p>
                </div>
            </div>
        )
    }

    return (
        <div ref={containerRef} className="absolute inset-0 overflow-hidden">
            <Map
                ref={mapRef}
                {...viewState}
                onMove={(evt) => setViewState(evt.viewState)}
                mapStyle={MAP_STYLES[mapStyle]}
                mapboxAccessToken={MAPBOX_TOKEN}
                style={{ width: "100%", height: "100%" }}
                terrain={{ source: "mapbox-dem", exaggeration: 1.5 }}
                fog={{
                    range: [0.5, 10],
                    color: "white",
                    "horizon-blend": 0.1,
                }}
            >
                {/* Navigation control hidden - using custom buttons instead */}

                {/* Terrain DEM source for 3D */}
                <Source
                    id="mapbox-dem"
                    type="raster-dem"
                    url="mapbox://mapbox.mapbox-terrain-dem-v1"
                    tileSize={512}
                    maxzoom={14}
                />

                {/* Site boundary from uploaded file */}
                {siteBoundary && Array.isArray(siteBoundary.coordinates) && siteBoundary.coordinates.length > 2 && (
                    <Source
                        id="site-boundary"
                        type="geojson"
                        data={{
                            type: "Feature",
                            geometry: {
                                type: "Polygon",
                                coordinates: (() => {
                                    const coords = Array.isArray(siteBoundary.coordinates) ? siteBoundary.coordinates : []
                                    if (coords.length < 3) return [[]]
                                    const mappedCoords = coords.map(c => [c?.longitude || 0, c?.latitude || 0])
                                    // Close the polygon
                                    mappedCoords.push([coords[0]?.longitude || 0, coords[0]?.latitude || 0])
                                    return [mappedCoords]
                                })()
                            },
                            properties: siteBoundary.properties || {}
                        } as GeoJSON.Feature}
                    >
                        {/* Fill layer */}
                        <Layer
                            id="site-boundary-fill"
                            type="fill"
                            paint={{
                                "fill-color": "#4CAF50",
                                "fill-opacity": 0.15,
                            }}
                        />
                        {/* Stroke layer */}
                        <Layer
                            id="site-boundary-stroke"
                            type="line"
                            paint={{
                                "line-color": "#4CAF50",
                                "line-width": 3,
                                "line-opacity": 0.9,
                            }}
                        />
                    </Source>
                )}

                {/* Layout data source */}
                {geoJSON && (
                    <Source id="layout-data" type="geojson" data={geoJSON as any}>
                        {/* Green spaces layer */}
                        <Layer
                            id="green-spaces-fill"
                            type="fill"
                            filter={["==", ["get", "layer"], "greenSpace"]}
                            paint={{
                                "fill-color": COLORS.greenSpace,
                                "fill-opacity": 0.6,
                            }}
                        />
                        <Layer
                            id="green-spaces-outline"
                            type="line"
                            filter={["==", ["get", "layer"], "greenSpace"]}
                            paint={{
                                "line-color": "#2E7D32",
                                "line-width": 2,
                            }}
                        />

                        {/* Roads layer */}
                        <Layer
                            id="roads-layer"
                            type="line"
                            filter={["==", ["get", "layer"], "roads"]}
                            paint={{
                                "line-color": ["get", "color"],
                                "line-width": ["get", "width"],
                                "line-opacity": 0.8,
                            }}
                            layout={{
                                "line-cap": "round",
                                "line-join": "round",
                            }}
                        />

                        {/* Parking layer */}
                        <Layer
                            id="parking-fill"
                            type="fill"
                            filter={["==", ["get", "layer"], "parking"]}
                            paint={{
                                "fill-color": ["get", "color"],
                                "fill-opacity": 0.7,
                            }}
                        />
                        <Layer
                            id="parking-outline"
                            type="line"
                            filter={["==", ["get", "layer"], "parking"]}
                            paint={{
                                "line-color": "#424242",
                                "line-width": 2,
                            }}
                        />

                        {/* Buildings layer - 3D extrusion */}
                        <Layer
                            id="buildings-3d"
                            type="fill-extrusion"
                            filter={["==", ["get", "layer"], "buildings"]}
                            paint={{
                                "fill-extrusion-color": ["get", "color"],
                                "fill-extrusion-height": ["*", ["get", "height"], 1],
                                "fill-extrusion-base": 0,
                                "fill-extrusion-opacity": 0.85,
                            }}
                        />

                        {/* Building labels */}
                        <Layer
                            id="building-labels"
                            type="symbol"
                            filter={["==", ["get", "layer"], "buildings"]}
                            layout={{
                                "text-field": ["get", "name"],
                                "text-size": 12,
                                "text-anchor": "center",
                                "text-offset": [0, 2],
                            }}
                            paint={{
                                "text-color": "#ffffff",
                                "text-halo-color": "#000000",
                                "text-halo-width": 1,
                            }}
                        />

                        {/* Utilities points */}
                        <Layer
                            id="utilities-circles"
                            type="circle"
                            filter={["==", ["get", "layer"], "utilities"]}
                            paint={{
                                "circle-radius": 10,
                                "circle-color": COLORS.utilities.power,
                                "circle-stroke-color": "#ffffff",
                                "circle-stroke-width": 2,
                            }}
                        />

                        {/* Fire protection points */}
                        <Layer
                            id="fire-circles"
                            type="circle"
                            filter={["==", ["get", "layer"], "fireProtection"]}
                            paint={{
                                "circle-radius": 8,
                                "circle-color": COLORS.fire,
                                "circle-stroke-color": "#ffffff",
                                "circle-stroke-width": 2,
                            }}
                        />
                    </Source>
                )}
            </Map>

            {/* Hover tooltip */}
            {hoveredItem && (
                <div
                    className="absolute bg-card/95 backdrop-blur-sm border-2 border-primary rounded-lg px-4 py-3 shadow-xl pointer-events-none z-50"
                    style={{ left: hoveredItem.x + 15, top: hoveredItem.y - 10 }}
                >
                    <div className="text-xs font-semibold text-primary uppercase mb-1">{hoveredItem.type}</div>
                    <div className="text-sm font-bold text-foreground">{hoveredItem.name}</div>
                    {hoveredItem.details && <div className="text-xs text-muted-foreground mt-1">{hoveredItem.details}</div>}
                </div>
            )}
        </div>
    )
}

export default MapboxCanvas
