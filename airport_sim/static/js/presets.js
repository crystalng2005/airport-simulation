
// Load presets when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadPresets();
});

async function loadPreset(presetId) {
    console.log(`Loading preset ${presetId} into config form...`);

    try {
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = 'Loading...';
        button.disabled = true;

        // Get preset data
        const response = await fetch(`/api/get-preset-data/${presetId}`);
        const data = await response.json();

        if (data.success) {
            button.innerHTML = 'Loaded!';
            
            // Create config object from preset
            const config = {
                runways: (data.vars.departure_runways || 0) + (data.vars.landing_runways || 0) + (data.vars.mixed_runways || 0),
                departure_runways: data.vars.departure_runways || 0,
                landing_runways: data.vars.landing_runways || 0,
                mixed_runways: data.vars.mixed_runways || 0,
                inbound_flow: 10,
                outbound_flow: 10,
                cancellation_time: 30,
                duration: 100
            };
            
            // Store in sessionStorage
            sessionStorage.setItem('presetConfig', JSON.stringify(config));
            
            // Redirect to config form
            setTimeout(() => {
                window.location.href = '/configure-simulation';
            }, 500);
        } else {
            alert('Error loading preset: ' + (data.error || 'Unknown error'));
            button.innerHTML = originalText;
            button.disabled = false;
        }
    } catch (error) {
        console.error('Error loading preset:', error);
        alert('Failed to load preset. Please try again.');
        event.target.innerHTML = 'Load This Preset';
        event.target.disabled = false;
    }
}

/**
 * Display preset cards in the grid
 * @param {Array} presets - Array of preset objects from backend
 */
function displayPresets(presets) {
    const presetsContainer = document.getElementById('presetsContainer');
    presetsContainer.innerHTML = ''; // Clear existing content

    // Sort by saved_at date (most recent first)
    presets.sort((a, b) => new Date(b.saved_at) - new Date(a.saved_at));

    // Only show top 3
    const top3Presets = presets.slice(0, 3);

    top3Presets.forEach((preset, index) => {
        const card = createPresetCard(preset, index);
        presetsContainer.appendChild(card);
    });
}

/**
 * Create a preset card element
 * @param {Object} preset - Preset data object
 * @param {Number} index - Index for labeling (0=Most Recent, 1=2nd, 2=3rd)
 */
function createPresetCard(preset, index) {
    const card = document.createElement('div');
    card.className = 'preset-card';

    const labels = ['Most Recent', '2nd Most Recent', '3rd Most Recent'];
    const presetLabel = labels[index] || `Preset ${index + 1}`;

    // Format date
    const savedDate = new Date(preset.saved_at);
    const formattedDate = savedDate.toLocaleString('en-GB', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    // Extract configuration data
    const vars = preset.vars || {};
    const report = preset.report || {};
    
    const totalRunways = (vars.departure_runways || 0) + 
                        (vars.landing_runways || 0) + 
                        (vars.mixed_runways || 0);

    card.innerHTML = `
        <div class="preset-header">
            <div class="preset-title">Preset ${preset.id + 1}</div>
            <div class="preset-badge">${presetLabel}</div>
        </div>

        <div class="preset-date"> Saved: ${formattedDate}</div>

        <!-- Runway Configuration -->
        <div class="preset-section">
            <div class="preset-section-title">Runway Configuration</div>
            <div class="preset-details">
                <div class="preset-detail-item">
                    <span class="detail-label">Total:</span>
                    <span class="detail-value">${totalRunways}</span>
                </div>
                <div class="preset-detail-item">
                    <span class="detail-label">Landing:</span>
                    <span class="detail-value">${vars.landing_runways || 0}</span>
                </div>
                <div class="preset-detail-item">
                    <span class="detail-label">Departure:</span>
                    <span class="detail-value">${vars.departure_runways || 0}</span>
                </div>
                <div class="preset-detail-item">
                    <span class="detail-label">Mixed:</span>
                    <span class="detail-value">${vars.mixed_runways || 0}</span>
                </div>
            </div>
        </div>

        <!-- Simulation Results Summary -->
        <div class="preset-section">
            <div class="preset-section-title">Simulation Results</div>
            <div class="results-summary">
                <div class="results-grid">
                    <div class="result-item">
                        <div class="result-value">${report.total_planes || 0}</div>
                        <div class="result-label">Total Planes</div>
                    </div>
                    <div class="result-item">
                        <div class="result-value">${report.diversions || 0}</div>
                        <div class="result-label">Diversions</div>
                    </div>
                    <div class="result-item">
                        <div class="result-value">${report.cancellations || 0}</div>
                        <div class="result-label">Cancellations</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Queue Statistics -->
        <div class="preset-section">
            <div class="preset-section-title">Queue Statistics</div>
            <div class="preset-details">
                <div class="preset-detail-item">
                    <span class="detail-label">Max Queue:</span>
                    <span class="detail-value">${report.queue_max || 0}</span>
                </div>
                <div class="preset-detail-item">
                    <span class="detail-label">Max Holding:</span>
                    <span class="detail-value">${report.holding_max || 0}</span>
                </div>
            </div>
        </div>

        <!-- Load Button -->
        <div class="load-button-container">
            <button class="btn-load" onclick="loadPreset(${preset.id})">
                Load This Preset
            </button>
        </div>
    `;

    return card;
}

/**
 * Load selected preset and start simulation
 * USES: VisualisationController.loadPresetIntoSimulation(presetId)
 * @param {Number} presetId - ID of the preset to load (0, 1, or 2)
 */
async function loadPreset(presetId) {
    console.log(`Loading preset ${presetId}...`);

    try {
        // Show loading state
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = 'Loading...';
        button.disabled = true;

        // PRESUMED METHOD: Send request to backend to load preset
        const response = await fetch('/api/load-preset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ preset_id: presetId })
        });

        const data = await response.json();

        if (data.success) {
            // Success! Redirect to simulation screen
            button.innerHTML = 'Loaded!';
            
            // Store preset ID in session for simulation screen to use
            sessionStorage.setItem('loadedPresetId', presetId);
            
            // Redirect to simulation screen after short delay
            setTimeout(() => {
                window.location.href = '/simulation';
            }, 1000);
        } else {
            // Error
            alert('Error loading preset: ' + (data.error || 'Unknown error'));
            button.innerHTML = originalText;
            button.disabled = false;
        }
    } catch (error) {
        console.error('Error loading preset:', error);
        alert('Failed to load preset. Please try again.');
        event.target.innerHTML = 'Load This Preset';
        event.target.disabled = false;
    }
}

/**
 * Navigate back to main menu
 */
function goToMenu() {
    window.location.href = '/';
}

/* ===================================
   
   PRESUMED VisualisationController METHODS:
   
   1. getAvailablePresets()
      - Returns list of the 3 most recent presets
      - Calls PresetController.getPresetSaveTimes()
      - Returns preset metadata
   
   2. getPresetData(presetId)
      - Returns full preset data for a specific preset
      - Calls PresetController.loadPreset(presetId)
      - Returns configuration, planes, and report data
   
   3. loadPresetIntoSimulation(presetId)
      - Loads preset into SimulationController
      - Restores runway configuration
      - Restores plane list
      - Prepares simulation to run with this preset
   
   =================================== */