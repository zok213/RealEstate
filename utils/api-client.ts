/**
 * API Client for Industrial Park Designer Backend
 */

import type {
    Project,
    DesignParameters,
    DesignJob,
    DesignVariant,
    ChatResponse,
    BackendLayout,
    ComplianceReport,
} from '@/types/api-types'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'

class ApiClient {
    private baseUrl: string

    constructor(baseUrl: string = BACKEND_URL) {
        this.baseUrl = baseUrl
    }

    private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`

        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
            throw new Error(error.detail || `API Error: ${response.status}`)
        }

        return response.json()
    }

    // ==================== PROJECT ENDPOINTS ====================

    async createProject(name: string = 'New Industrial Park', siteAreaHa: number = 50): Promise<Project> {
        const response = await this.request<{ project_id: string; project: any }>('/api/projects/new', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                site_area_ha: siteAreaHa
            }),
        })
        return {
            id: response.project_id,
            name: response.project.name,
            created_at: response.project.created_at,
            parameters: {} as DesignParameters,
        }
    }

    async getProject(projectId: string): Promise<Project> {
        return this.request<Project>(`/api/projects/${projectId}`)
    }

    // ==================== CHAT ENDPOINTS ====================

    async sendChatMessage(projectId: string, message: string): Promise<ChatResponse> {
        const response = await this.request<{
            response: string;
            extracted_params?: any;
            ready_for_design: boolean;
            model_used: string;
        }>('/api/chat', {
            method: 'POST',
            body: JSON.stringify({ project_id: projectId, message: message }),
        })

        return {
            content: response.response,
            extracted_params: response.extracted_params,
            ready_for_generation: response.ready_for_design,
            model_used: response.model_used,
        }
    }

    // ==================== DESIGN GENERATION ENDPOINTS ====================

    async startDesignGeneration(projectId: string, parameters: DesignParameters): Promise<{ job_id: string }> {
        return this.request<{ job_id: string }>('/api/designs/generate', {
            method: 'POST',
            body: JSON.stringify({ project_id: projectId, parameters: parameters }),
        })
    }

    async getJobStatus(jobId: string): Promise<DesignJob> {
        return this.request<DesignJob>(`/api/designs/jobs/${jobId}`)
    }

    async getDesignVariants(projectId: string): Promise<DesignVariant[]> {
        const response = await this.request<{ variants: DesignVariant[] }>(`/api/designs/${projectId}/variants`)
        return response.variants || []
    }

    async waitForJob(
        jobId: string,
        onProgress?: (progress: number, step?: string) => void,
        maxAttempts: number = 60,
        intervalMs: number = 2000
    ): Promise<DesignJob> {
        for (let i = 0; i < maxAttempts; i++) {
            const job = await this.getJobStatus(jobId)
            if (onProgress && job.progress !== undefined) {
                onProgress(job.progress, job.current_step)
            }
            if (job.status === 'completed' || job.status === 'failed') return job
            await new Promise(resolve => setTimeout(resolve, intervalMs))
        }
        throw new Error('Job timed out')
    }

    // ==================== EXPORT ENDPOINTS ====================

    async exportDXF(variantId: string, projectId: string): Promise<Blob> {
        const response = await fetch(`${this.baseUrl}/api/export/${projectId}/${variantId}?format=dxf`)
        if (!response.ok) throw new Error('Export failed')
        return response.blob()
    }

    downloadFile(blob: Blob, filename: string): void {
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
    }

    // ==================== COMPLIANCE ENDPOINTS ====================

    async getComplianceReport(variantId: string): Promise<ComplianceReport> {
        return this.request<ComplianceReport>(`/api/compliance/${variantId}`)
    }

    // ==================== DXF UPLOAD & ANALYSIS ====================

    async uploadAndAnalyzeDXF(file: File, projectId?: string): Promise<any> {
        const formData = new FormData()
        formData.append('file', file)
        if (projectId) {
            formData.append('project_id', projectId)
        }

        const url = `${this.baseUrl}/api/upload-dxf${projectId ? `?project_id=${projectId}` : ''}`
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
            throw new Error(error.detail || `Upload Error: ${response.status}`)
        }

        return response.json()
    }
}

export const apiClient = new ApiClient()
export { ApiClient }
