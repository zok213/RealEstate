"use client"

import React, { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { apiClient } from '@/utils/api-client'
import type {
    Project,
    DesignParameters,
    DesignVariant,
    BackendLayout,
} from '@/types/api-types'
import type { IndustrialParkLayout } from '@/types/industrial-park'
import type { SiteBoundary, SiteInfo } from '@/utils/file-parsers'

interface DesignContextType {
    // Project state
    currentProject: Project | null
    setCurrentProject: (project: Project | null) => void

    // Site boundary from file upload
    siteBoundary: SiteBoundary | null
    setSiteBoundary: (boundary: SiteBoundary | null) => void
    siteInfo: SiteInfo | null
    setSiteInfo: (info: SiteInfo | null) => void

    // Design variants
    variants: DesignVariant[]
    selectedVariant: DesignVariant | null
    selectVariant: (variant: DesignVariant) => void

    // Current layout for map display
    currentLayout: IndustrialParkLayout | null

    // Design generation
    isGenerating: boolean
    generationProgress: number
    generationStep: string
    generateDesigns: (params: DesignParameters) => Promise<void>

    // Chat extracted params
    extractedParams: DesignParameters | null
    setExtractedParams: (params: DesignParameters | null) => void
    readyForGeneration: boolean

    // Export
    exportDXF: (variantId: string) => Promise<void>
    isExporting: boolean

    // Errors
    error: string | null
    clearError: () => void
}

const DesignContext = createContext<DesignContextType | undefined>(undefined)

// Convert backend layout to frontend format
function convertBackendToFrontendLayout(backend: BackendLayout): IndustrialParkLayout {
    // Safety: ensure all arrays exist
    const roads = backend?.roads || []
    const buildings = backend?.buildings || []
    const greenSpaces = backend?.green_spaces || []
    const parking = backend?.parking || []
    const utilities = backend?.utilities || []
    const fireProtection = backend?.fire_protection || []

    return {
        id: `layout-${Date.now()}`,
        name: 'Generated Layout',
        totalArea: 500000, // Will be calculated from site boundary
        metadata: {
            createdAt: new Date(),
            updatedAt: new Date(),
            version: '1.0',
        },
        roads: roads.map(road => ({
            id: road.id,
            name: road.name,
            type: road.type,
            coordinates: (road.coordinates || []).map(c => ({ longitude: c.longitude, latitude: c.latitude })),
            width: road.width,
        })),
        buildings: buildings.map(building => ({
            id: building.id,
            name: building.name,
            type: building.type as "manufacturing" | "warehouse" | "office" | "utility" | "mixed",
            coordinates: { longitude: building.coordinates?.longitude || 0, latitude: building.coordinates?.latitude || 0 },
            size: building.size,
            floors: building.floors,
            zones: building.interior_zones || { production: 0.5, office: 0.2, storage: 0.3 },
        })),
        greenSpaces: greenSpaces.map(space => ({
            id: space.id,
            type: space.type,
            coordinates: (space.coordinates || []).map(c => ({ longitude: c.longitude, latitude: c.latitude })),
            area: space.area,
            trees: space.trees || 20,
        })),
        parking: parking.map(p => ({
            id: p.id,
            type: p.type,
            coordinates: { longitude: p.coordinates?.longitude || 0, latitude: p.coordinates?.latitude || 0 },
            spaces: p.spaces,
            rows: p.rows,
            cols: p.cols,
        })),
        utilities: utilities.map(u => ({
            id: u.id,
            type: u.type,
            label: u.name,
            coordinates: { longitude: u.coordinates?.longitude || 0, latitude: u.coordinates?.latitude || 0 },
            capacity: u.capacity || 'N/A',
        })),
        fireProtection: fireProtection.map(f => ({
            id: f.id,
            type: f.type,
            label: f.name,
            coordinates: { longitude: f.coordinates?.longitude || 0, latitude: f.coordinates?.latitude || 0 },
        })),
    }
}

export function DesignProvider({ children }: { children: ReactNode }) {
    // State
    const [currentProject, setCurrentProject] = useState<Project | null>(null)
    const [siteBoundary, setSiteBoundary] = useState<SiteBoundary | null>(null)
    const [siteInfo, setSiteInfo] = useState<SiteInfo | null>(null)
    const [variants, setVariants] = useState<DesignVariant[]>([])
    const [selectedVariant, setSelectedVariant] = useState<DesignVariant | null>(null)
    const [currentLayout, setCurrentLayout] = useState<IndustrialParkLayout | null>(null)
    const [isGenerating, setIsGenerating] = useState(false)
    const [generationProgress, setGenerationProgress] = useState(0)
    const [generationStep, setGenerationStep] = useState<string>('')
    const [extractedParams, setExtractedParams] = useState<DesignParameters | null>(null)
    const [isExporting, setIsExporting] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const readyForGeneration = extractedParams !== null &&
        extractedParams.totalArea_ha > 0 &&
        Array.isArray(extractedParams.industryFocus) &&
        extractedParams.industryFocus.length > 0

    // Select a variant and update layout
    const selectVariant = useCallback((variant: DesignVariant) => {
        setSelectedVariant(variant)
        if (variant.layout) {
            const frontendLayout = convertBackendToFrontendLayout(variant.layout)
            setCurrentLayout(frontendLayout)
        }
    }, [])

    // Generate designs using backend
    const generateDesigns = useCallback(async (params: DesignParameters) => {
        try {
            setIsGenerating(true)
            setGenerationProgress(0)
            setError(null)

            // Create project if not exists
            let project = currentProject
            if (!project) {
                project = await apiClient.createProject(params.projectName || 'Industrial Park')
                setCurrentProject(project)
            }

            // Start generation job
            const { job_id } = await apiClient.startDesignGeneration(project.id, params)

            // Poll for completion
            const job = await apiClient.waitForJob(
                job_id,
                (progress, step) => {
                    setGenerationProgress(progress)
                    if (step) setGenerationStep(step)
                }
            )

            if (job.status === 'failed') {
                throw new Error(job.error || 'Design generation failed')
            }

            // Fetch variants
            const newVariants = await apiClient.getDesignVariants(project.id)
            setVariants(newVariants)

            // Auto-select best variant
            if (newVariants.length > 0) {
                const best = newVariants.reduce((a, b) => a.score > b.score ? a : b)
                selectVariant(best)
            }

            setGenerationProgress(100)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error')
        } finally {
            setIsGenerating(false)
        }
    }, [currentProject, selectVariant])

    // Export DXF
    const exportDXF = useCallback(async (variantId: string) => {
        if (!currentProject) return

        try {
            setIsExporting(true)
            const blob = await apiClient.exportDXF(variantId, currentProject.id)
            apiClient.downloadFile(blob, `design_${variantId}.dxf`)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Export failed')
        } finally {
            setIsExporting(false)
        }
    }, [currentProject])

    const clearError = useCallback(() => setError(null), [])

    const value: DesignContextType = {
        currentProject,
        setCurrentProject,
        siteBoundary,
        setSiteBoundary,
        siteInfo,
        setSiteInfo,
        variants,
        selectedVariant,
        selectVariant,
        currentLayout,
        isGenerating,
        generationProgress,
        generationStep,
        generateDesigns,
        extractedParams,
        setExtractedParams,
        readyForGeneration,
        exportDXF,
        isExporting,
        error,
        clearError,
    }

    return (
        <DesignContext.Provider value={value}>
            {children}
        </DesignContext.Provider>
    )
}

export function useDesign() {
    const context = useContext(DesignContext)
    if (context === undefined) {
        throw new Error('useDesign must be used within a DesignProvider')
    }
    return context
}
