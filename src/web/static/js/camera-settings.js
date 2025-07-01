/**
 * Camera settings management for the smart wheelchair control system
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const ipCameraUrlInput = document.getElementById('ip-camera-url');
    const testConnectionBtn = document.getElementById('test-camera-connection');
    const connectionStatusDiv = document.getElementById('camera-connection-status');
    const saveSettingsBtn = document.getElementById('save-settings');
    
    // Test camera connection
    if (testConnectionBtn) {
        testConnectionBtn.addEventListener('click', function() {
            const cameraUrl = ipCameraUrlInput.value.trim();
            
            if (!cameraUrl) {
                showConnectionStatus('error', 'Please enter a valid camera URL');
                return;
            }
            
            // Show testing message
            showConnectionStatus('info', 'Testing connection...');
            
            // Try to fetch a test image from the camera
            fetch(cameraUrl + '/shot.jpg', { 
                method: 'GET',
                mode: 'no-cors', // This is needed for cross-origin requests
                cache: 'no-cache',
                headers: {
                    'Accept': 'image/jpeg'
                },
                timeout: 5000
            })
            .then(response => {
                if (response.type === 'opaque') {
                    // no-cors mode doesn't let us access the response status
                    // but if we got here, at least the request didn't fail
                    showConnectionStatus('success', 'Connection successful! Camera is accessible.');
                } else if (response.ok) {
                    showConnectionStatus('success', 'Connection successful! Camera is accessible.');
                } else {
                    showConnectionStatus('error', `Connection failed: ${response.status} ${response.statusText}`);
                }
            })
            .catch(error => {
                showConnectionStatus('error', `Connection failed: ${error.message}`);
            });
        });
    }
    
    // Save camera settings
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', function() {
            const cameraUrl = ipCameraUrlInput.value.trim();
            
            if (!cameraUrl) {
                showConnectionStatus('error', 'Please enter a valid camera URL');
                return;
            }
            
            // Send the new URL to the server
            fetch('/api/camera/update-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: cameraUrl })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('success', 'Camera URL updated successfully');
                    // Reload the page to apply the new URL
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    showNotification('error', `Failed to update camera URL: ${data.message}`);
                }
            })
            .catch(error => {
                showNotification('error', `Error: ${error.message}`);
            });
        });
    }
    
    // Helper function to show connection status
    function showConnectionStatus(type, message) {
        if (connectionStatusDiv) {
            connectionStatusDiv.innerHTML = '';
            
            const alertClass = type === 'success' ? 'alert-success' : 
                              type === 'error' ? 'alert-danger' : 
                              'alert-info';
            
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert ${alertClass} mt-2`;
            alertDiv.textContent = message;
            
            connectionStatusDiv.appendChild(alertDiv);
        }
    }
    
    // Helper function to show notifications
    function showNotification(type, message) {
        const notificationArea = document.getElementById('notification-area') || 
                               document.createElement('div');
        
        if (!document.getElementById('notification-area')) {
            notificationArea.id = 'notification-area';
            notificationArea.style.position = 'fixed';
            notificationArea.style.top = '20px';
            notificationArea.style.right = '20px';
            notificationArea.style.zIndex = '9999';
            document.body.appendChild(notificationArea);
        }
        
        const notification = document.createElement('div');
        notification.className = `alert ${type === 'success' ? 'alert-success' : 'alert-danger'} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        notificationArea.appendChild(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notificationArea.removeChild(notification);
            }, 500);
        }, 5000);
    }
});
