
// Sample configuration data (in real app, this comes from the simulation)
let currentConfig = {
    totalRunways: 5,
    landingRunways: 2,
    departureRunways: 2,
    mixedRunways: 1,
    landingPerHour: 10,
    departurePerHour: 10,
    totalPlanes: 50,
    simulationDuration: 8
};

// Load configuration data when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadConfigurationData();
});

/**
 * Load configuration data from session/localStorage or URL parameters
 */
function loadConfigurationData() {
    // Try to get data from sessionStorage (set by previous page)
    const storedConfig = sessionStorage.getItem('simulationConfig');
    
    if (storedConfig) {
        currentConfig = JSON.parse(storedConfig);
    }
    
    // Update the display
    updateConfigDisplay();
}

/**
 * Update the displayed configuration values
 */
function updateConfigDisplay() {
    document.getElementById('totalRunways').textContent = currentConfig.totalRunways;
    document.getElementById('landingRunways').textContent = currentConfig.landingRunways;
    document.getElementById('departureRunways').textContent = currentConfig.departureRunways;
    document.getElementById('mixedRunways').textContent = currentConfig.mixedRunways;
    document.getElementById('landingPerHour').textContent = currentConfig.landingPerHour + ' per hour';
    document.getElementById('departurePerHour').textContent = currentConfig.departurePerHour + ' per hour';
    document.getElementById('totalPlanes').textContent = currentConfig.totalPlanes;
    document.getElementById('simTime').textContent = currentConfig.simulationDuration + ' hours';
}

/**
 * Save the preset
 */
function savePreset() {
    const presetName = document.getElementById('presetName').value.trim();
    
    // Create preset data object
    const presetData = {
        name: presetName || generatePresetName(),
        timestamp: new Date().toISOString(),
        config: currentConfig
    };
    
    // Show loading state
    const saveBtn = document.querySelector('.btn-save');
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<span class="btn-icon">⏳</span> Saving...';
    saveBtn.disabled = true;
    
    // Send to backend
    fetch('/api/save-preset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(presetData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            document.getElementById('successMessage').style.display = 'flex';
            
            // Reset button
            saveBtn.innerHTML = '<span class="btn-icon">✅</span> Saved!';
            
            // Redirect back to menu after 2 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            alert('Error saving preset: ' + data.error);
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving preset. Please try again.');
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    });
}

/**
 * Generate automatic preset name with timestamp
 */
function generatePresetName() {
    const now = new Date();
    const date = now.toLocaleDateString('en-GB').replace(/\//g, '-');
    const time = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    return `Preset ${date} ${time}`;
}

/**
 * Cancel and go back
 */
function cancelSave() {
    if (confirm('Are you sure you want to cancel? Your configuration will not be saved.')) {
        window.location.href = '/';
    }
}

/**
 * Alternative: Saves to localStorage (if backend not ready)
 */
function savePresetLocally() {
    const presetName = document.getElementById('presetName').value.trim();
    
    // Get existing presets
    let presets = JSON.parse(localStorage.getItem('airportPresets') || '[]');
    
    // Create new preset
    const newPreset = {
        id: Date.now(),
        name: presetName || generatePresetName(),
        timestamp: new Date().toISOString(),
        config: currentConfig
    };
    
    // Add to beginning of array
    presets.unshift(newPreset);
    
    // Keep only last 3 presets
    if (presets.length > 3) {
        presets = presets.slice(0, 3);
    }
    
    // Save back to localStorage
    localStorage.setItem('airportPresets', JSON.stringify(presets));
    
    // Show success
    document.getElementById('successMessage').style.display = 'flex';
    
    // Redirect
    setTimeout(() => {
        window.location.href = '/';
    }, 2000);
}