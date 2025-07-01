// Camera page functionality
$(document).ready(function() {
    // Get current camera info on page load
    updateCameraStatus();
    
    // Refresh stream button
    $('#refresh-connection').click(function() {
        updateCameraStatus();
    });
    
    // Edit camera URL
    $('#edit-camera-url').click(function() {
        // Show editor
        $('#camera-url-editor').removeClass('d-none');
        // Get current URL without http:// prefix
        let currentUrl = $('#current-camera-url').val();
        currentUrl = currentUrl.replace('http://', '');
        $('#edit-url-input').val(currentUrl);
    });
    
    // Cancel edit
    $('#cancel-url-edit').click(function() {
        $('#camera-url-editor').addClass('d-none');
    });
    
    // Save new URL
    $('#save-url-button').click(function() {
        const newUrl = $('#edit-url-input').val();
        updateCameraUrl(newUrl);
    });
    
    // Update camera URL (from error panel)
    $('#update-camera-url').click(function() {
        const newUrl = $('#new-camera-url').val();
        updateCameraUrl(newUrl);
    });
    
    // Take snapshot
    $('#take-snapshot').click(function() {
        $.ajax({
            url: '/api/camera/snapshot',
            type: 'GET',
            success: function(data) {
                if (data.success) {
                    showToast('Success', 'Snapshot saved to: ' + data.path, 'success');
                } else {
                    showToast('Error', 'Failed to save snapshot: ' + data.error, 'danger');
                }
            }
        });
    });
    
    // Camera source switching
    $('#use-ip-camera').click(function() {
        $(this).addClass('active').siblings().removeClass('active');
        $('#stream-image').attr('src', '/api/camera/stream');
        showToast('Camera Changed', 'Switched to Wi-Fi camera', 'info');
    });
    
    $('#use-usb-camera').click(function() {
        $(this).addClass('active').siblings().removeClass('active');
        $('#stream-image').attr('src', '/api/camera/usb_stream');
        
        $.ajax({
            url: '/api/camera/use_usb',
            type: 'POST',
            success: function(data) {
                if (data.success) {
                    showToast('Camera Changed', 'Switched to USB camera', 'success');
                } else {
                    showToast('Warning', data.message, 'warning');
                }
            }
        });
    });
    
    // Scan network for cameras
    $('#scan-network').click(function() {
        $(this).prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Scanning...');
        
        $.ajax({
            url: '/api/camera/scan',
            type: 'GET',
            success: function(data) {
                $('#scan-network').prop('disabled', false).text('Scan Network for Cameras');
                
                const foundCameras = $('#found-cameras');
                foundCameras.empty();
                
                if (data.cameras && data.cameras.length > 0) {
                    foundCameras.removeClass('d-none');
                    
                    data.cameras.forEach(function(camera) {
                        // Extract just the host:port part
                        const url = camera.replace('http://', '');
                        
                        const item = $('<button>')
                            .addClass('list-group-item list-group-item-action camera-option')
                            .attr('data-url', url)
                            .text(url);
                        
                        foundCameras.append(item);
                    });
                } else {
                    foundCameras.removeClass('d-none');
                    foundCameras.append(
                        $('<div>')
                            .addClass('list-group-item text-center')
                            .text('No cameras found')
                    );
                }
            },
            error: function() {
                $('#scan-network').prop('disabled', false).text('Scan Network for Cameras');
                showToast('Error', 'Failed to scan network', 'danger');
            }
        });
    });
    
    // Use a found camera
    $(document).on('click', '.camera-option', function() {
        const url = $(this).attr('data-url');
        $('#new-camera-url').val(url);
        updateCameraUrl(url);
    });
    
    // Movement controls
    $('#move-forward').on('mousedown touchstart', function() { sendMoveCommand('forward'); });
    $('#move-backward').on('mousedown touchstart', function() { sendMoveCommand('backward'); });
    $('#turn-left').on('mousedown touchstart', function() { sendMoveCommand('left'); });
    $('#turn-right').on('mousedown touchstart', function() { sendMoveCommand('right'); });
    $('#stop-motors').on('click', function() { sendMoveCommand('stop'); });
    
    // Stop on mouse up/touch end
    $('.btn-circle').on('mouseup mouseleave touchend touchcancel', function() {
        sendMoveCommand('stop');
    });
    
    // Periodically update camera status and stream
    setInterval(function() {
        // Only update the image if the connection-error is hidden (camera is working)
        if ($('#connection-error').hasClass('d-none')) {
            refreshStreamImage();
        }
    }, 500);
    
    setInterval(function() {
        updateCameraStatus();
    }, 5000);
});

// Function to update camera URL
function updateCameraUrl(newUrl) {
    // Show loading state
    const saveBtn = $('#save-url-button');
    const updateBtn = $('#update-camera-url');
    saveBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Saving...');
    updateBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Updating...');
    
    $.ajax({
        url: '/api/camera/update',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ url: newUrl }),
        success: function(data) {
            // Reset buttons
            saveBtn.prop('disabled', false).text('Save');
            updateBtn.prop('disabled', false).text('Update');
            
            // Hide editor
            $('#camera-url-editor').addClass('d-none');
            
            // Update status
            if (data.success || data.available) {
                showToast('Success', 'Camera URL updated successfully', 'success');
                updateCameraStatus();
            } else {
                showToast('Warning', 'Camera URL updated but connection failed', 'warning');
                updateCameraStatus();
            }
        },
        error: function() {
            // Reset buttons
            saveBtn.prop('disabled', false).text('Save');
            updateBtn.prop('disabled', false).text('Update');
            
            showToast('Error', 'Failed to update camera URL', 'danger');
        }
    });
}

// Function to update camera status
function updateCameraStatus() {
    $.ajax({
        url: '/api/camera/status',
        type: 'GET',
        success: function(data) {
            // Update current URL display
            $('#current-camera-url').val(data.url);
            
            // Show/hide error message based on availability
            if (data.available) {
                $('#connection-error').addClass('d-none');
                $('#camera-feed').removeClass('d-none');
                refreshStreamImage();
            } else {
                $('#connection-error').removeClass('d-none');
                $('#camera-feed').addClass('d-none');
            }
        }
    });
}

// Function to refresh the stream image
function refreshStreamImage() {
    const img = $('#stream-image');
    const currentSrc = img.attr('src');
    
    // Add timestamp to prevent caching
    if (currentSrc.indexOf('?') === -1) {
        img.attr('src', currentSrc + '?t=' + new Date().getTime());
    } else {
        img.attr('src', currentSrc.split('?')[0] + '?t=' + new Date().getTime());
    }
}

// Send movement command to server
function sendMoveCommand(direction) {
    $.ajax({
        url: '/api/motors/' + direction,
        type: 'POST',
        data: JSON.stringify({ speed: 50 }),
        contentType: 'application/json',
        success: function(data) {
            console.log('Movement command sent:', direction);
        }
    });
}

// Function to show toast notification
function showToast(title, message, type) {
    // Create toast container if it doesn't exist
    if ($('.toast-container').length === 0) {
        $('body').append('<div class="toast-container position-fixed bottom-0 end-0 p-3"></div>');
    }

    const toast = $(`
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `);
    
    $('.toast-container').append(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}
