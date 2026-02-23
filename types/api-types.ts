/**
 * API Types for Industrial Park Designer Backend
 */

// Project types
export interface Project {
    id: string
    name: string
    created_at: string
    parameters: DesignParameters
}

// Design parameters from AI chat
export interface DesignParameters {
    projectName?: string
    totalArea_ha: number
    industryFocus: IndustryFocus[]
    workerCapacity: number
    constraints: DesignConstraints
    specialRequirements?: string[]
}

export interface IndustryFocus {
    type: 'light_manufacturing' | 'medium_manufacturing' | 'heavy_manufacturing' | 'warehouse' | 'logistics'
    count: number
    percentage: number
}

export interface DesignConstraints {
    greenAreaMin_percent: number
    roadAreaMin_percent: number
    minBuildingSpacing_m: number
}

// Job types for async design generation
export interface DesignJob {
    job_id: string
    status: 'pending' | 'running' | 'completed' | 'failed'
    progress?: number
    current_step?: string
    timings?: {
        building_generation?: number
        csp_solver?: number
        ga_optimizer?: number
        compliance_check?: number
        total?: number
    }
    result?: DesignResult
    error?: string
}

export interface DesignResult {
    variants: DesignVariant[]
    compliance: ComplianceReport
}

// Design variant from backend
export interface DesignVariant {
    id: string
    name: string
    score: number
    layout: BackendLayout
    metrics: DesignMetrics
    compliance?: {
        overall_score: number
        overall_status: 'pass' | 'warning' | 'fail'
        details?: Record<string, {
            label: string
            passed: boolean
            detail: string
        }>
    }
}

export interface DesignMetrics {
    road_efficiency: number
    worker_flow: number
    green_ratio: number
    space_utilization: number
}

// Backend layout format
export interface BackendLayout {
    site_boundary: Coordinate[]
    buildings: BackendBuilding[]
    roads: BackendRoad[]
    green_spaces: BackendGreenSpace[]
    parking: BackendParking[]
    utilities: BackendUtility[]
    fire_protection: BackendFireProtection[]
}

export interface Coordinate {
    longitude: number
    latitude: number
}

export interface BackendBuilding {
    id: string
    name: string
    type: string
    coordinates: Coordinate
    size: [number, number] // [width, height] in meters
    floors: number
    area_m2: number
    interior_zones?: Record<string, number>
}

export interface BackendRoad {
    id: string
    name: string
    type: 'primary' | 'secondary' | 'industrial' | 'service' | 'fire'
    coordinates: Coordinate[]
    width: number
}

export interface BackendGreenSpace {
    id: string
    type: 'park' | 'greenBelt' | 'buffer'
    coordinates: Coordinate[]
    area: number
    trees?: number
}

export interface BackendParking {
    id: string
    type: 'car' | 'truck'
    coordinates: Coordinate
    spaces: number
    rows: number
    cols: number
}

export interface BackendUtility {
    id: string
    type: 'powerSubstation' | 'waterTreatment' | 'waterStorage' | 'wasteCollection' | 'sewage'
    name: string
    coordinates: Coordinate
    capacity?: string
}

export interface BackendFireProtection {
    id: string
    type: 'hydrant' | 'station'
    name: string
    coordinates: Coordinate
}

// Compliance report from backend
export interface ComplianceReport {
    overall_score: number
    overall_status: 'pass' | 'warning' | 'fail'
    checks: ComplianceCheck[]
    recommendations: string[]
}

export interface ComplianceCheck {
    category: string
    name: string
    status: 'pass' | 'warning' | 'fail'
    score: number
    details: string
    required_value?: string
    actual_value?: string
}

// Chat response with extracted params
export interface ChatResponse {
    content: string
    extracted_params?: DesignParameters
    ready_for_generation: boolean
    model_used: string
}

// Export types
export interface ExportRequest {
    variant_id: string
    format: 'dxf' | 'json' | 'geojson'
}

export interface ExportResponse {
    download_url: string
    filename: string
}
