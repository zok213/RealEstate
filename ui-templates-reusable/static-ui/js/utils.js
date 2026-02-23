/**
 * Navigation utilities for DXF Land Parser
 */

// Navigation functions
function navigateToDashboard() {
    window.location.href = '/';
}

function navigateToUpload() {
    window.location.href = '/upload';
}

function navigateToEstate(estateId) {
    window.location.href = `/estate/${estateId}`;
}

function navigateToMap(estateId) {
    window.location.href = `/map/${estateId}`;
}

// Get session ID from URL
function getSessionIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    return pathParts[pathParts.length - 1];
}

// Format numbers
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(Math.round(num));
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0
    }).format(amount);
}

function formatArea(area) {
    return `${formatNumber(area)} m²`;
}

// Status badge helper
function getStatusBadge(status) {
    const badges = {
        'available': '<span class="badge-available px-3 py-1 rounded-full text-xs font-bold">Available</span>',
        'sold': '<span class="badge-sold px-3 py-1 rounded-full text-xs font-bold">Sold</span>',
        'reserved': '<span class="badge-reserved px-3 py-1 rounded-full text-xs font-bold">Reserved</span>'
    };
    return badges[status] || status;
}

// Show loading indicator
function showLoading(message = 'Loading...') {
    const loader = document.createElement('div');
    loader.id = 'global-loader';
    loader.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';
    loader.innerHTML = `
        <div class="bg-surface-dark p-8 rounded-2xl border border-surface-border flex flex-col items-center gap-4">
            <div class="loading"></div>
            <p class="text-white font-medium">${message}</p>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.remove();
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-xl border flex items-center gap-3 animate-fade-in ${
        type === 'success' ? 'bg-green-500/10 border-green-500 text-green-500' :
        type === 'error' ? 'bg-red-500/10 border-red-500 text-red-500' :
        'bg-blue-500/10 border-blue-500 text-blue-500'
    }`;
    
    const icon = type === 'success' ? 'check_circle' : type === 'error' ? 'error' : 'info';
    notification.innerHTML = `
        <span class="material-symbols-outlined">${icon}</span>
        <span class="font-medium">${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Confirm dialog
function confirm(message, callback) {
    const dialog = document.createElement('div');
    dialog.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';
    dialog.innerHTML = `
        <div class="bg-surface-dark p-6 rounded-2xl border border-surface-border max-w-md">
            <h3 class="text-xl font-bold text-white mb-4">Confirm</h3>
            <p class="text-gray-300 mb-6">${message}</p>
            <div class="flex gap-3 justify-end">
                <button id="cancel-btn" class="px-6 py-2 rounded-full bg-surface-border text-white font-bold hover:bg-opacity-80">
                    Cancel
                </button>
                <button id="confirm-btn" class="px-6 py-2 rounded-full bg-primary text-background-dark font-bold hover:bg-opacity-90">
                    Confirm
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialog);
    
    document.getElementById('cancel-btn').addEventListener('click', () => {
        dialog.remove();
    });
    
    document.getElementById('confirm-btn').addEventListener('click', () => {
        dialog.remove();
        callback();
    });
}

// Local storage helpers
const Storage = {
    get(key) {
        try {
            return JSON.parse(localStorage.getItem(key));
        } catch {
            return null;
        }
    },
    
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch {
            return false;
        }
    },
    
    remove(key) {
        localStorage.removeItem(key);
    }
};

// Export utilities
window.Utils = {
    navigateToDashboard,
    navigateToUpload,
    navigateToEstate,
    navigateToMap,
    getSessionIdFromUrl,
    formatNumber,
    formatCurrency,
    formatArea,
    getStatusBadge,
    showLoading,
    hideLoading,
    showNotification,
    confirm,
    Storage
};
