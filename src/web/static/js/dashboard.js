document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const motorToggle = document.getElementById('motor-toggle');
    const speedControl = document.getElementById('speed-control');
    const speedValue = document.getElementById('speed-value');
    const motorStatus = document.getElementById('motor-status');
    const directionStatus = document.getElementById('direction-status');
    const speedStatus = document.getElementById('speed-status');
    const distanceValue = document.getElementById('distance-value');
    const distanceIndicator = document.getElementById('distance-indicator');
    const directionButtons = document.querySelectorAll('.direction-btn');
    const forwardBtn = document.getElementById('forward-btn');
    const backwardBtn = document.getElementById('backward-btn');
    const leftBtn = document.getElementById('left-btn');
    const rightBtn = document.getElementById('right-btn');
    const stopBtn = document.getElementById('stop-btn');
    const cameraFeed = document.getElementById('camera-feed');
    const noCameraMessage = document.getElementById('no-camera-message');
    const joystickInfo = document.getElementById('joystick-info');
    
    // Tab navigation
    const dashboardTab = document.getElementById('dashboard-tab');
    const cameraTab = document.getElementById('camera-tab');
    const settingsTab = document.getElementById('settings-tab');
    const aboutTab = document.getElementById('about-tab');
    
    const dashboardContent = document.getElementById('dashboard-content');
    const settingsContent = document.getElementById('settings-content');
    const aboutContent = document.getElementById('about-content');
    
    // State
    let motorRunning = false;
    let currentSpeed = 50;
    let currentDirection = 'stop';
    let updateInterval = 500; // milliseconds
    let updateTimer = null;
    let joystick = null;
    let joystickPosition = { x: 0, y: 0 };
    
    // GPS Variables
    let gpsUpdateInterval;
    let lastGpsData = null;
    let map = null;
    let marker = null;
    
    // Initialize joystick
    createJoystick();
    
    // Check if camera is available
    checkCameraAvailability();
    
    // Set up event listeners
    motorToggle.addEventListener('click', toggleMotors);
    speedControl.addEventListener('input', updateSpeedDisplay);
    speedControl.addEventListener('change', setSpeed);
    forwardBtn.addEventListener('click', () => setDirection('forward'));
    backwardBtn.addEventListener('click', () => setDirection('backward'));
    leftBtn.addEventListener('click', () => setDirection('left'));
    rightBtn.addEventListener('click', () => setDirection('right'));
    stopBtn.addEventListener('click', () => setDirection('stop'));
    
    // Tab navigation
    dashboardTab.addEventListener('click', showDashboard);
    cameraTab.addEventListener('click', showCamera);
    settingsTab.addEventListener('click', showSettings);
    aboutTab.addEventListener('click', showAbout);
    
    // Start updates
    startUpdates();
    
    /**
     * Initialize the virtual joystick
     */
    function createJoystick() {
        const options = {
            zone: document.getElementById('joystick-zone'),
            mode: 'static',
            position: { left: '50%', top: '50%' },
            color: 'blue',
            size: 150
        };
        
        joystick = nipplejs.create(options);
        
        joystick.on('move', function(evt, data) {
            const x = parseFloat(data.vector.x).toFixed(2);
            const y = parseFloat(-data.vector.y).toFixed(2);
            
            joystickPosition = { x, y };
            joystickInfo.textContent = `X: ${x}, Y: ${y}`;
            
            // Only send joystick updates when motors are running
            if (motorRunning) {
                sendJoystickCommand(x, y);
            }
        });
        
        joystick.on('end', function() {
            joystickPosition = { x: 0, y: 0 };
            joystickInfo.textContent = `X: 0, Y: 0`;
            
            // Stop the motors if they're running
            if (motorRunning) {
                setDirection('stop');
            }
        });
    }
    
    /**
     * Send joystick position to control motors
     */
    function sendJoystickCommand(x, y) {
        fetch('/api/motors/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: 'joystick',
                speed: currentSpeed,
                x: x,
                y: y
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update UI if needed
            }
        })
        .catch(error => {
            console.error('Error sending joystick command:', error);
        });
    }
    
    /**
     * Toggle motors on/off
     */
    function toggleMotors() {
        const command = motorRunning ? 'stop' : 'start';
        
        fetch('/api/motors/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: command,
                speed: currentSpeed
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                motorRunning = !motorRunning;
                updateMotorUI();
            }
        })
        .catch(error => {
            console.error('Error toggling motors:', error);
        });
    }
    
    /**
     * Update speed display as the slider moves
     */
    function updateSpeedDisplay() {
        const speed = speedControl.value;
        speedValue.textContent = speed;
        speedStatus.textContent = `${speed}%`;
    }
    
    /**
     * Set motor speed
     */
    function setSpeed() {
        currentSpeed = parseInt(speedControl.value);
        
        if (motorRunning) {
            fetch('/api/motors/control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    command: currentDirection,
                    speed: currentSpeed
                })
            })
            .catch(error => {
                console.error('Error setting speed:', error);
            });
        }
    }
    
    /**
     * Set motor direction
     */
    function setDirection(direction) {
        if (!motorRunning && direction !== 'stop') {
            return; // Don't change direction if motors aren't running
        }
        
        currentDirection = direction;
        
        fetch('/api/motors/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: direction,
                speed: currentSpeed
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateDirectionUI(direction);
            }
        })
        .catch(error => {
            console.error('Error setting direction:', error);
        });
    }
    
    /**
     * Update motor UI based on running state
     */
    function updateMotorUI() {
        if (motorRunning) {
            motorToggle.classList.remove('btn-success');
            motorToggle.classList.add('btn-danger');
            motorToggle.innerHTML = '<i class="bi bi-power me-2"></i>Stop Motors';
            
            motorStatus.textContent = 'Running';
            motorStatus.classList.remove('bg-secondary');
            motorStatus.classList.add('bg-success');
            
            // Enable direction buttons
            directionButtons.forEach(btn => {
                btn.disabled = false;
            });
        } else {
            motorToggle.classList.remove('btn-danger');
            motorToggle.classList.add('btn-success');
            motorToggle.innerHTML = '<i class="bi bi-power me-2"></i>Start Motors';
            
            motorStatus.textContent = 'Stopped';
            motorStatus.classList.remove('bg-success');
            motorStatus.classList.add('bg-secondary');
            
            // Disable direction buttons
            directionButtons.forEach(btn => {
                btn.disabled = true;
            });
            
            // Reset direction
            updateDirectionUI('stop');
        }
    }
    
    /**
     * Update UI elements for direction change
     */
    function updateDirectionUI(direction) {
        // Remove active class from all direction buttons
        forwardBtn.classList.remove('active', 'btn-dark');
        backwardBtn.classList.remove('active', 'btn-dark');
        leftBtn.classList.remove('active', 'btn-dark');
        rightBtn.classList.remove('active', 'btn-dark');
        stopBtn.classList.remove('active', 'btn-danger');
        
        forwardBtn.classList.add('btn-outline-dark');
        backwardBtn.classList.add('btn-outline-dark');
        leftBtn.classList.add('btn-outline-dark');
        rightBtn.classList.add('btn-outline-dark');
        stopBtn.classList.add('btn-outline-danger');
        
        // Set the active button based on direction
        let directionText = 'None';
        let badgeColor = 'bg-secondary';
        
        switch (direction) {
            case 'forward':
                forwardBtn.classList.add('active', 'btn-dark');
                forwardBtn.classList.remove('btn-outline-dark');
                directionText = 'Forward';
                badgeColor = 'bg-primary';
                break;
            case 'backward':
                backwardBtn.classList.add('active', 'btn-dark');
                backwardBtn.classList.remove('btn-outline-dark');
                directionText = 'Backward';
                badgeColor = 'bg-primary';
                break;
            case 'left':
                leftBtn.classList.add('active', 'btn-dark');
                leftBtn.classList.remove('btn-outline-dark');
                directionText = 'Left';
                badgeColor = 'bg-primary';
                break;
            case 'right':
                rightBtn.classList.add('active', 'btn-dark');
                rightBtn.classList.remove('btn-outline-dark');
                directionText = 'Right';
                badgeColor = 'bg-primary';
                break;
            case 'stop':
                stopBtn.classList.add('active', 'btn-danger');
                stopBtn.classList.remove('btn-outline-danger');
                directionText = 'Stopped';
                badgeColor = 'bg-secondary';
                break;
            case 'joystick':
                directionText = 'Joystick';
                badgeColor = 'bg-info';
                break;
        }
        
        directionStatus.textContent = directionText;
        directionStatus.className = `badge ${badgeColor}`;
    }
    
    /**
     * Check if camera is available
     */
    function checkCameraAvailability() {
        cameraFeed.onerror = function() {
            cameraFeed.classList.add('d-none');
            noCameraMessage.classList.remove('d-none');
        };
    }
    
    /**
     * Tab navigation - show dashboard
     */
    function showDashboard(e) {
        e.preventDefault();
        setActiveTab(dashboardTab);
        
        dashboardContent.classList.remove('d-none');
        settingsContent.classList.add('d-none');
        aboutContent.classList.add('d-none');
    }
    
    /**
     * Tab navigation - show camera fullscreen
     */
    function showCamera(e) {
        e.preventDefault();
        setActiveTab(cameraTab);
        
        // Implement fullscreen camera view logic
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            const cameraContainer = document.querySelector('.camera-container');
            if (cameraContainer.requestFullscreen) {
                cameraContainer.requestFullscreen();
            }
        }
    }
    
    /**
     * Tab navigation - show settings
     */
    function showSettings(e) {
        e.preventDefault();
        setActiveTab(settingsTab);
        
        dashboardContent.classList.add('d-none');
        settingsContent.classList.remove('d-none');
        aboutContent.classList.add('d-none');
    }
    
    /**
     * Tab navigation - show about
     */
    function showAbout(e) {
        e.preventDefault();
        setActiveTab(aboutTab);
        
        dashboardContent.classList.add('d-none');
        settingsContent.classList.add('d-none');
        aboutContent.classList.remove('d-none');
    }
    
    /**
     * Set active tab
     */
    function setActiveTab(activeTab) {
        // Remove active class from all tabs
        dashboardTab.classList.remove('active');
        cameraTab.classList.remove('active');
        settingsTab.classList.remove('active');
        aboutTab.classList.remove('active');
        
        // Add active class to selected tab
        activeTab.classList.add('active');
    }
    
    /**
     * Start periodic updates of sensor data
     */
    function startUpdates() {
        if (updateTimer) {
            clearInterval(updateTimer);
        }
        
        updateData();
        updateTimer = setInterval(updateData, updateInterval);
    }
    
    /**
     * Update sensor data from API
     */
    function updateData() {
        // Get motor status
        fetch('/api/motors/status')
            .then(response => response.json())
            .then(data => {
                motorRunning = data.running;
                currentSpeed = data.speed;
                currentDirection = data.direction;
                
                // Update UI to reflect current state
                speedControl.value = currentSpeed;
                updateSpeedDisplay();
                updateMotorUI();
                updateDirectionUI(currentDirection);
            })
            .catch(error => {
                console.error('Error fetching motor status:', error);
            });
        
        // Get distance sensor data
        fetch('/api/sensors/distance')
            .then(response => response.json())
            .then(data => {
                if (data.distance !== undefined) {
                    const distance = data.distance;
                    distanceValue.textContent = `${distance} cm`;
                    
                    // Update distance indicator (percentage based on 0-100cm range)
                    const percentage = Math.min(100, Math.max(0, 100 - distance));
                    distanceIndicator.style.width = `${percentage}%`;
                    
                    // Color coding for distance
                    if (distance < 15) {
                        distanceIndicator.className = 'progress-bar bg-danger';
                    } else if (distance < 30) {
                        distanceIndicator.className = 'progress-bar bg-warning';
                    } else {
                        distanceIndicator.className = 'progress-bar bg-success';
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching sensor data:', error);
            });
    }
    
    // Initialize GPS functionality
    function initGPS() {
        // Start GPS data updates
        updateGpsData();
        gpsUpdateInterval = setInterval(updateGpsData, 5000);
        
        // Save location button
        document.getElementById('save-location').addEventListener('click', function() {
            saveCurrentLocation();
        });
        
        // Initialize map if available (we'll use a simple link to Google Maps)
        initializeMap();
    }
    
    // Update GPS data from server
    function updateGpsData() {
        fetch('/api/gps/formatted')
            .then(response => response.json())
            .then(data => {
                // Update GPS status
                const statusIndicator = document.getElementById('gps-status-indicator');
                const statusText = document.getElementById('gps-status-text');
                const statusDescription = document.getElementById('gps-status-description');
                
                // Update status indicator based on GPS status
                statusIndicator.className = 'status-circle me-2';
                switch (data.status) {
                    case 'active':
                        statusIndicator.classList.add('bg-gps-active');
                        statusText.textContent = 'Active';
                        break;
                    case 'no_fix':
                    case 'connected':
                        statusIndicator.classList.add('bg-gps-connecting');
                        statusText.textContent = 'Connecting';
                        break;
                    case 'disconnected':
                    case 'error':
                        statusIndicator.classList.add('bg-gps-error');
                        statusText.textContent = 'Error';
                        break;
                    default:
                        statusIndicator.classList.add('bg-secondary');
                        statusText.textContent = 'Unknown';
                }
                
                // Update status description
                statusDescription.textContent = data.status_description || 'No information available';
                
                // Update coordinates and other info
                document.getElementById('gps-coordinates').textContent = data.coordinates || '--';
                document.getElementById('gps-speed').textContent = data.speed || '--';
                document.getElementById('gps-altitude').textContent = data.altitude || '--';
                document.getElementById('gps-satellites').textContent = data.satellites || '--';
                
                // Save data for map
                lastGpsData = data;
                
                // Update the map if coordinates are available
                updateMapIfAvailable();
            })
            .catch(error => {
                console.error('Error fetching GPS data:', error);
            });
    }
    
    // Initialize map or show relevant message
    function initializeMap() {
        const mapContainer = document.getElementById('map-container');
        const statusMessage = document.getElementById('map-status-message');
        
        // Check if browser supports geolocation
        if (!navigator.geolocation) {
            statusMessage.textContent = 'Geolocation is not supported by your browser';
            return;
        }
        
        // Create a link to Google Maps using current wheelchair location
        statusMessage.textContent = 'Waiting for GPS coordinates...';
    }
    
    // Update map with GPS coordinates
    function updateMapIfAvailable() {
        if (!lastGpsData || lastGpsData.status !== 'active' || 
            lastGpsData.coordinates === 'Unknown' || 
            !lastGpsData.coordinates.includes(',')) {
            return;
        }
        
        // Extract lat and lng
        const coordParts = lastGpsData.coordinates.split(',');
        if (coordParts.length !== 2) return;
        
        // Parse latitude and longitude
        const latMatch = coordParts[0].match(/(\d+\.\d+)°\s*([NS])/);
        const lngMatch = coordParts[1].match(/(\d+\.\d+)°\s*([EW])/);
        
        if (!latMatch || !lngMatch) return;
        
        const lat = parseFloat(latMatch[1]) * (latMatch[2] === 'N' ? 1 : -1);
        const lng = parseFloat(lngMatch[1]) * (lngMatch[2] === 'E' ? 1 : -1);
        
        // Set up a Google Maps link
        const mapContainer = document.getElementById('map-container');
        const noMapMessage = document.getElementById('no-map-message');
        
        if (noMapMessage) {
            // Replace the loading message with a link to Google Maps
            mapContainer.innerHTML = `
                <div class="text-center pt-4">
                    <p>GPS coordinates: ${lastGpsData.coordinates}</p>
                    <a href="https://www.google.com/maps?q=${lat},${lng}" 
                       target="_blank" class="btn btn-primary">
                        <i class="bi bi-map"></i> View on Google Maps
                    </a>
                    <div class="mt-3">
                        <img src="https://maps.googleapis.com/maps/api/staticmap?center=${lat},${lng}&zoom=15&size=600x300&markers=color:red%7C${lat},${lng}&key=YOUR_API_KEY" 
                             alt="Static Map" class="img-fluid" style="max-width: 100%; border-radius: 5px;">
                    </div>
                </div>
            `;
        }
    }
    
    // Save current location
    function saveCurrentLocation() {
        if (!lastGpsData || lastGpsData.status !== 'active') {
            alert('Cannot save location: No valid GPS coordinates available');
            return;
        }
        
        // Prompt for a label
        const label = prompt('Enter a name for this location:', 'Home');
        if (label === null) return; // User canceled
        
        // Send save request
        fetch('/api/gps/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ label: label })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Location saved: ' + data.message);
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error saving location:', error);
            alert('Error saving location. See console for details.');
        });
    }
    
    // Add GPS initialization to your main init function
    document.addEventListener('DOMContentLoaded', function() {
        // Your existing initialization code
        
        // Initialize GPS functionality
        initGPS();
    });
    
    // Clean up GPS interval on page unload
    window.addEventListener('beforeunload', function() {
        if (gpsUpdateInterval) {
            clearInterval(gpsUpdateInterval);
        }
    });
    
    // Update obstacle information
    function updateObstacleInfo() {
      $.ajax({
        url: '/api/obstacles',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
          if (data.distance) {
            $('#obstacle-distance').text(data.distance.toFixed(1));
            
            // Update warning level
            const level = data.warning_level;
            const detected = data.detected;
            const autoStop = data.auto_stop_triggered;
            
            $('#obstacle-warning-level').text(level.charAt(0).toUpperCase() + level.slice(1));
            
            // Update badge and progress bar
            const badge = $('#obstacle-status-badge');
            const progress = $('#obstacle-progress');
            
            if (level === 'danger') {
              badge.attr('class', 'badge bg-danger').text('DANGER');
              progress.attr('class', 'progress-bar bg-danger').css('width', '100%');
              $('#obstacle-message').text('DANGER: Motors stopped - obstacle too close!');
            } else if (level === 'warning') {
              badge.attr('class', 'badge bg-warning text-dark').text('WARNING');
              progress.attr('class', 'progress-bar bg-warning').css('width', '75%');
              $('#obstacle-message').text('Warning: Obstacle detected - proceed with caution');
            } else if (level === 'caution') {
              badge.attr('class', 'badge bg-info text-dark').text('CAUTION');
              progress.attr('class', 'progress-bar bg-info').css('width', '50%');
              $('#obstacle-message').text('Caution: Obstacle in range - be aware');
            } else {
              badge.attr('class', 'badge bg-success').text('CLEAR');
              progress.attr('class', 'progress-bar bg-success').css('width', '25%');
              $('#obstacle-message').text('Path is clear');
            }
            
            // Add warning animation if obstacle detected
            if (detected) {
              badge.addClass('blink');
            } else {
              badge.removeClass('blink');
            }
          }
        },
        error: function(xhr, status, error) {
          console.error('Error getting obstacle data:', error);
        }
      });
    }
    
    // Add to your document ready function:
    $(document).ready(function() {
      // Existing code...
      
      // Update data periodically
      setInterval(function() {
        updateSensorData();
        updateMotorStatus();
        updateObstacleInfo();
      }, 1000);
    });
});

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
    
    // Update camera URL (old interface)
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

// Function to show toast notification
function showToast(title, message, type) {
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