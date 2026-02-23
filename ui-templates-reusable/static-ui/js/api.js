/**
 * API Client for DXF Land Parser
 * Handles all backend communication
 */

const API_BASE_URL = window.location.origin;

// API Client
const API = {
    // Health check
    async health() {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        return response.json();
    },

    // Upload DXF file
    async uploadDXF(file, onProgress) {
        return new Promise((resolve, reject) => {
            const formData = new FormData();
            formData.append('file', file);

            const xhr = new XMLHttpRequest();

            // Progress tracking
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
            }

            // Success handler
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    resolve(response);
                } else {
                    reject(new Error(`Upload failed with status: ${xhr.status}`));
                }
            });

            // Error handler
            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed'));
            });

            xhr.open('POST', `${API_BASE_URL}/api/upload-dxf`);
            xhr.send(formData);
        });
    },

    // Get session info
    async getSession(sessionId) {
        const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}`);
        if (!response.ok) {
            throw new Error(`Failed to get session: ${response.status}`);
        }
        return response.json();
    },

    // Generate layouts
    async generateLayouts(sessionId, targetPlots = 8, setback = 50.0) {
        const response = await fetch(`${API_BASE_URL}/api/generate-layouts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                target_plots: targetPlots,
                setback: setback
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to generate layouts: ${response.status}`);
        }
        return response.json();
    },

    // Chat with AI
    async chat(sessionId, message) {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`Chat failed: ${response.status}`);
        }
        return response.json();
    },

    // Export DXF
    async exportDXF(sessionId, optionId) {
        const response = await fetch(`${API_BASE_URL}/api/export-dxf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                option_id: optionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`Export failed: ${response.status}`);
        }
        
        // Download the file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `layout_${optionId}_${Date.now()}.dxf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    },

    // Export all DXFs as ZIP
    async exportAllDXF(sessionId) {
        const formData = new FormData();
        formData.append('session_id', sessionId);

        const response = await fetch(`${API_BASE_URL}/api/export-all-dxf`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Export failed: ${response.status}`);
        }
        
        // Download the ZIP file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `layouts_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
};

// Export for use in other scripts
window.API = API;
