// LPU Campus Management System - Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeSystem();
});

function initializeSystem() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize auto-dismiss alerts
    initAutoDismissAlerts();
    
    // Initialize responsive sidebar
    initResponsiveSidebar();
    
    // Initialize AJAX functionality
    initAjaxFeatures();
}

function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initFormValidation() {
    // Enable Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

function initAutoDismissAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

function initResponsiveSidebar() {
    // Handle sidebar collapse on mobile
    const sidebar = document.querySelector('.sidebar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    
    if (navbarToggler && sidebar) {
        navbarToggler.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (event) => {
        const isMobile = window.innerWidth < 992;
        const sidebar = document.querySelector('.sidebar');
        const navbarToggler = document.querySelector('.navbar-toggler');
        
        if (isMobile && sidebar && !sidebar.contains(event.target) && 
            navbarToggler && !navbarToggler.contains(event.target)) {
            sidebar.classList.remove('collapsed');
        }
    });
}

function initAjaxFeatures() {
    // Handle AJAX form submissions
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
    
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';
            submitBtn.disabled = true;
            
            fetch(this.action, {
                method: this.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Success', data.message, 'success');
                    if (data.redirect) {
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 1500);
                    }
                } else {
                    showToast('Error', data.message, 'error');
                }
            })
            .catch(error => {
                showToast('Error', 'An error occurred. Please try again.', 'error');
            })
            .finally(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    });
}

function showToast(title, message, type = 'info') {
    // Create toast notification
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto text-${type}">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Utility function for making AJAX requests
function makeAjaxRequest(url, method = 'GET', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => response.json());
}

// Real-time clock for dashboard
function initDashboardClock() {
    const clockElement = document.getElementById('dashboard-clock');
    if (clockElement) {
        function updateClock() {
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            });
            const dateString = now.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            clockElement.innerHTML = `
                <div class="text-center">
                    <div class="h3 mb-1">${timeString}</div>
                    <div class="small text-muted">${dateString}</div>
                </div>
            `;
        }
        
        updateClock();
        setInterval(updateClock, 1000);
    }
}

// Attendance status updater
function updateAttendanceStatus() {
    const statusElements = document.querySelectorAll('[data-attendance-status]');
    
    statusElements.forEach(element => {
        const status = element.getAttribute('data-attendance-status');
        const studentId = element.getAttribute('data-student-id');
        
        if (status === 'present') {
            element.classList.add('status-present');
        } else if (status === 'absent') {
            element.classList.add('status-absent');
        } else {
            element.classList.add('status-pending');
        }
    });
}

// Export to Excel with loading state
function exportToExcel(button, url) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading-spinner"></span> Exporting...';
    button.disabled = true;
    
    setTimeout(() => {
        window.location.href = url;
        button.innerHTML = originalText;
        button.disabled = false;
    }, 1000);
}

// Initialize all features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSystem();
    initDashboardClock();
    updateAttendanceStatus();
});

// Add global error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showToast('JavaScript Error', 'An unexpected error occurred. Please refresh the page.', 'error');
});

// Add offline/online detection
window.addEventListener('online', function() {
    showToast('Connection Restored', 'You are back online.', 'success');
});

window.addEventListener('offline', function() {
    showToast('Connection Lost', 'You are currently offline. Some features may not work.', 'warning');
});