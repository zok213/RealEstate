/**
 * Estate Navigation Helper
 * Handles dynamic navigation between estate detail pages
 */

(function() {
    'use strict';

    // Get current estate ID from URL
    function getCurrentEstateId() {
        const path = window.location.pathname;
        const match = path.match(/\/estate\/([^\/]+)/);
        return match ? match[1] : null;
    }

    // Navigate to estate tab
    function navigateToEstateTab(tab) {
        const estateId = getCurrentEstateId();
        if (!estateId) {
            console.error('No estate ID found in URL');
            return;
        }

        const urls = {
            'overview': `/estate/${estateId}`,
            'map': `/map/${estateId}`,
            'plots': `/plots/${estateId}`,
            'fullscreen': `/fullscreen-map/${estateId}`
        };

        if (urls[tab]) {
            window.location.href = urls[tab];
        }
    }

    // Update tab links on page load
    function updateTabLinks() {
        const estateId = getCurrentEstateId();
        if (!estateId) return;

        // Find all tab links
        const tabs = document.querySelectorAll('[data-estate-tab]');
        tabs.forEach(tab => {
            const tabName = tab.getAttribute('data-estate-tab');
            const urls = {
                'overview': `/estate/${estateId}`,
                'map': `/map/${estateId}`,
                'plots': `/plots/${estateId}`
            };
            
            if (urls[tabName]) {
                tab.href = urls[tabName];
            }
        });
    }

    // Export functions
    window.EstateNav = {
        getCurrentEstateId,
        navigateToTab: navigateToEstateTab,
        updateTabLinks
    };

    // Auto-update on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateTabLinks);
    } else {
        updateTabLinks();
    }
})();
