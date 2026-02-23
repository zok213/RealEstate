/**
 * Estate Detail Page Logic
 * Loads and displays estate information from API
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Get session ID from URL
    const pathParts = window.location.pathname.split('/');
    const sessionId = pathParts[pathParts.length - 1];

    if (!sessionId) {
        alert('No session ID provided');
        window.location.href = '/';
        return;
    }

    try {
        // Load session data
        const session = await API.getSession(sessionId);
        console.log('Session data:', session);

        // Update page with session data
        if (session.metadata) {
            // Update area
            const areaElement = document.querySelector('[data-area]');
            if (areaElement && session.metadata.area) {
                areaElement.textContent = Math.round(session.metadata.area).toLocaleString() + ' m²';
            }

            // Update perimeter
            const perimeterElement = document.querySelector('[data-perimeter]');
            if (perimeterElement && session.metadata.perimeter) {
                perimeterElement.textContent = Math.round(session.metadata.perimeter).toLocaleString() + ' m';
            }

            // Update centroid for map if available
            if (session.metadata.centroid) {
                window.estateCentroid = session.metadata.centroid;
            }
        }

        // Store session for other pages
        sessionStorage.setItem('currentSession', JSON.stringify(session));

        // If layouts exist, show them
        if (session.layouts && session.layouts.length > 0) {
            displayLayouts(session.layouts);
        }

    } catch (error) {
        console.error('Error loading session:', error);
        alert('Failed to load estate data');
    }
});

function displayLayouts(layouts) {
    // Display generated layouts if any
    console.log('Layouts:', layouts);
    // TODO: Implement layout display
}

// Generate layouts button handler
async function generateLayouts() {
    const pathParts = window.location.pathname.split('/');
    const sessionId = pathParts[pathParts.length - 1];

    try {
        const result = await API.generateLayouts(sessionId);
        console.log('Generated layouts:', result);
        alert(`Successfully generated ${result.count} layout options!`);
        
        // Reload page to show layouts
        window.location.reload();
    } catch (error) {
        console.error('Error generating layouts:', error);
        alert('Failed to generate layouts');
    }
}

// Export for use in HTML onclick handlers
window.generateLayouts = generateLayouts;
