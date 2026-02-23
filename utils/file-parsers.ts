/**
 * File Parser Utilities for DXF and GeoJSON
 */

import DxfParser from 'dxf-parser'
import type { GeoCoordinate } from '@/types/industrial-park'

// ==================== TYPES ====================

export interface SiteBoundary {
    coordinates: GeoCoordinate[]
    properties?: {
        name?: string
        area_m2?: number
        perimeter_m?: number
        layer?: string
    }
}

export interface SiteInfo {
    filename: string
    format: 'dxf' | 'dwg' | 'geojson' | 'kml' | 'unknown'
    area_ha: number
    area_m2: number
    perimeter_m: number
    bounds: {
        minLat: number
        maxLat: number
        minLon: number
        maxLon: number
    }
    center: GeoCoordinate
    layers?: string[]
    entities?: number
}

export interface ParseResult {
    success: boolean
    boundary: SiteBoundary | null
    info: SiteInfo | null
    error?: string
    rawData?: any
}

// ==================== GEOJSON PARSER ====================

export function parseGeoJSON(content: string, filename: string): ParseResult {
    try {
        const data = JSON.parse(content)

        // Handle FeatureCollection or single Feature
        let feature
        if (data.type === 'FeatureCollection') {
            // Find the first polygon feature
            feature = data.features?.find((f: any) =>
                f.geometry?.type === 'Polygon' || f.geometry?.type === 'MultiPolygon'
            )
        } else if (data.type === 'Feature') {
            feature = data
        } else if (data.type === 'Polygon' || data.type === 'MultiPolygon') {
            feature = { type: 'Feature', geometry: data, properties: {} }
        }

        if (!feature || !feature.geometry) {
            return { success: false, boundary: null, info: null, error: 'No polygon found in GeoJSON' }
        }

        // Extract coordinates
        let coords: [number, number][]
        if (feature.geometry.type === 'Polygon') {
            coords = feature.geometry.coordinates[0] // Outer ring
        } else if (feature.geometry.type === 'MultiPolygon') {
            coords = feature.geometry.coordinates[0][0] // First polygon's outer ring
        } else {
            return { success: false, boundary: null, info: null, error: 'Geometry must be Polygon or MultiPolygon' }
        }

        // Convert to GeoCoordinate array
        const geoCoords: GeoCoordinate[] = coords.map(([lon, lat]) => ({
            longitude: lon,
            latitude: lat,
        }))

        // Calculate area and perimeter
        const area_m2 = calculatePolygonArea(geoCoords)
        const perimeter_m = calculatePerimeter(geoCoords)
        const bounds = calculateBounds(geoCoords)
        const center = calculateCenter(bounds)

        const boundary: SiteBoundary = {
            coordinates: geoCoords,
            properties: {
                name: feature.properties?.name || filename,
                area_m2,
                perimeter_m,
            }
        }

        const info: SiteInfo = {
            filename,
            format: 'geojson',
            area_ha: area_m2 / 10000,
            area_m2,
            perimeter_m,
            bounds,
            center,
        }

        return { success: true, boundary, info, rawData: data }
    } catch (e) {
        return { success: false, boundary: null, info: null, error: `GeoJSON parse error: ${e}` }
    }
}

// ==================== DXF PARSER ====================

export function parseDXF(content: string, filename: string, referencePoint?: GeoCoordinate): ParseResult {
    try {
        const parser = new DxfParser()
        const dxf = parser.parseSync(content)

        if (!dxf || !dxf.entities) {
            return { success: false, boundary: null, info: null, error: 'Invalid DXF file' }
        }

        // Find polyline entities (LWPOLYLINE or POLYLINE)
        const polylines = dxf.entities.filter((e: any) =>
            e.type === 'LWPOLYLINE' || e.type === 'POLYLINE' || e.type === 'LINE'
        ) as any[]

        if (polylines.length === 0) {
            return { success: false, boundary: null, info: null, error: 'No polylines found in DXF' }
        }

        // Find the largest polyline (assume it's the site boundary)
        let largestPolyline: any = polylines[0]
        let maxArea = 0

        for (const poly of polylines) {
            if (poly.vertices && poly.vertices.length > 2) {
                const vertices = poly.vertices.map((v: any) => ({ x: v.x, y: v.y }))
                const area = calculateXYArea(vertices)
                if (area > maxArea) {
                    maxArea = area
                    largestPolyline = poly
                }
            }
        }

        // Extract vertices
        const vertices = largestPolyline.vertices || []
        if (vertices.length < 3) {
            return { success: false, boundary: null, info: null, error: 'Polyline has less than 3 vertices' }
        }

        // Convert DXF coordinates (meters) to geo coordinates
        // Default reference point: Hanoi area
        const refPoint = referencePoint || { latitude: 21.0285, longitude: 105.8542 }

        const geoCoords: GeoCoordinate[] = vertices.map((v: any) => {
            // Approximate conversion: 1 degree ≈ 111,320 meters at equator
            // Adjusted for latitude
            const latOffset = v.y / 111320
            const lonOffset = v.x / (111320 * Math.cos(refPoint.latitude * Math.PI / 180))

            return {
                latitude: refPoint.latitude + latOffset,
                longitude: refPoint.longitude + lonOffset,
            }
        })

        // Close the polygon if not closed
        if (geoCoords.length > 0 &&
            (geoCoords[0].latitude !== geoCoords[geoCoords.length - 1].latitude ||
                geoCoords[0].longitude !== geoCoords[geoCoords.length - 1].longitude)) {
            geoCoords.push({ ...geoCoords[0] })
        }

        // Calculate metrics in DXF units (meters)
        const area_m2 = maxArea
        const perimeter_m = calculateXYPerimeter(vertices)
        const bounds = calculateBounds(geoCoords)
        const center = calculateCenter(bounds)

        // Get layers
        const layers = [...new Set(dxf.entities.map((e: any) => e.layer).filter(Boolean))]

        const boundary: SiteBoundary = {
            coordinates: geoCoords,
            properties: {
                name: filename,
                area_m2,
                perimeter_m,
                layer: largestPolyline.layer,
            }
        }

        const info: SiteInfo = {
            filename,
            format: 'dxf',
            area_ha: area_m2 / 10000,
            area_m2,
            perimeter_m,
            bounds,
            center,
            layers: layers as string[],
            entities: dxf.entities.length,
        }

        return { success: true, boundary, info, rawData: dxf }
    } catch (e) {
        return { success: false, boundary: null, info: null, error: `DXF parse error: ${e}` }
    }
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Calculate polygon area using Shoelace formula with Haversine for geo coords
 */
function calculatePolygonArea(coords: GeoCoordinate[]): number {
    if (coords.length < 3) return 0

    // Convert to approximate meters and use shoelace
    const center = {
        lat: coords.reduce((s, c) => s + c.latitude, 0) / coords.length,
        lon: coords.reduce((s, c) => s + c.longitude, 0) / coords.length,
    }

    const metersPerDegreeLat = 111320
    const metersPerDegreeLon = 111320 * Math.cos(center.lat * Math.PI / 180)

    const points = coords.map(c => ({
        x: (c.longitude - center.lon) * metersPerDegreeLon,
        y: (c.latitude - center.lat) * metersPerDegreeLat,
    }))

    return calculateXYArea(points)
}

/**
 * Calculate area from XY coordinates using Shoelace formula
 */
function calculateXYArea(points: { x: number; y: number }[]): number {
    if (points.length < 3) return 0

    let area = 0
    const n = points.length

    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n
        area += points[i].x * points[j].y
        area -= points[j].x * points[i].y
    }

    return Math.abs(area / 2)
}

/**
 * Calculate perimeter from geo coordinates
 */
function calculatePerimeter(coords: GeoCoordinate[]): number {
    if (coords.length < 2) return 0

    let perimeter = 0
    for (let i = 0; i < coords.length - 1; i++) {
        perimeter += haversineDistance(coords[i], coords[i + 1])
    }

    return perimeter
}

/**
 * Calculate perimeter from XY coordinates
 */
function calculateXYPerimeter(points: { x: number; y: number }[]): number {
    if (points.length < 2) return 0

    let perimeter = 0
    for (let i = 0; i < points.length - 1; i++) {
        const dx = points[i + 1].x - points[i].x
        const dy = points[i + 1].y - points[i].y
        perimeter += Math.sqrt(dx * dx + dy * dy)
    }

    // Close the polygon
    if (points.length > 2) {
        const dx = points[0].x - points[points.length - 1].x
        const dy = points[0].y - points[points.length - 1].y
        perimeter += Math.sqrt(dx * dx + dy * dy)
    }

    return perimeter
}

/**
 * Haversine distance between two points in meters
 */
function haversineDistance(p1: GeoCoordinate, p2: GeoCoordinate): number {
    const R = 6371000 // Earth radius in meters
    const lat1 = p1.latitude * Math.PI / 180
    const lat2 = p2.latitude * Math.PI / 180
    const dLat = (p2.latitude - p1.latitude) * Math.PI / 180
    const dLon = (p2.longitude - p1.longitude) * Math.PI / 180

    const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

    return R * c
}

/**
 * Calculate bounding box
 */
function calculateBounds(coords: GeoCoordinate[]) {
    const lats = coords.map(c => c.latitude)
    const lons = coords.map(c => c.longitude)

    return {
        minLat: Math.min(...lats),
        maxLat: Math.max(...lats),
        minLon: Math.min(...lons),
        maxLon: Math.max(...lons),
    }
}

/**
 * Calculate center point
 */
function calculateCenter(bounds: ReturnType<typeof calculateBounds>): GeoCoordinate {
    return {
        latitude: (bounds.minLat + bounds.maxLat) / 2,
        longitude: (bounds.minLon + bounds.maxLon) / 2,
    }
}

// ==================== MAIN PARSER ====================

export async function parseFile(file: File): Promise<ParseResult> {
    const filename = file.name.toLowerCase()

    // Handle DWG files - need backend conversion
    if (filename.endsWith('.dwg')) {
        return parseDWG(file)
    }
    
    // Parse text-based formats
    const content = await file.text()

    if (filename.endsWith('.geojson') || filename.endsWith('.json')) {
        return parseGeoJSON(content, file.name)
    } else if (filename.endsWith('.dxf')) {
        return parseDXF(content, file.name)
    } else {
        return {
            success: false,
            boundary: null,
            info: null,
            error: `Unsupported file format: ${file.name}`
        }
    }
}

/**
 * Parse DWG file by converting to DXF via backend
 * Backend will attempt auto-conversion, fallback to instructions if fails
 */
async function parseDWG(file: File): Promise<ParseResult> {
    try {
        // Upload to backend for auto-conversion
        const formData = new FormData()
        formData.append('file', file)
        
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'
        const response = await fetch(`${backendUrl}/api/convert/dwg-to-dxf`, {
            method: 'POST',
            body: formData,
        })
        
        // Success - backend converted DWG to DXF
        if (response.ok && response.headers.get('content-type')?.includes('dxf')) {
            const dxfContent = await response.text()
            
            // Parse the converted DXF
            const result = parseDXF(dxfContent, file.name)
            
            // Update format to dwg and add success message
            if (result.info) {
                result.info.format = 'dwg'
            }
            
            return {
                ...result,
                // Add conversion success note
            }
        }
        
        // Backend returns 501 with manual instructions (conversion failed)
        if (response.status === 501) {
            const errorData = await response.json()
            const instructions = errorData.instructions?.map((i: string) => i).join('\n') || ''
            return {
                success: false,
                boundary: null,
                info: null,
                error: `❌ ${errorData.message}\n\n📝 Hướng dẫn convert:\n${instructions}\n\n${errorData.auto_conversion || ''}\n\n${errorData.alternative || '💡 Dùng online converter'}`
            }
        }
        
        if (!response.ok) {
            throw new Error(`Conversion failed: ${response.statusText}`)
        }
        
        // Unexpected response
        throw new Error('Unexpected response format')
        
    } catch (error) {
        return {
            success: false,
            boundary: null,
            info: null,
            error: `❌ Lỗi xử lý file DWG: ${error}\n\n💡 Giải pháp:\n1. Convert sang DXF bằng AutoCAD/LibreCAD\n2. Hoặc dùng: https://convertio.co/vn/dwg-dxf/\n3. Upload file DXF đã convert`
        }
    }
}
