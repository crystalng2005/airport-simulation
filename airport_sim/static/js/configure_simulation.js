
// Initialise on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add validation listeners
    const runwayInputs = document.querySelectorAll(
        '#departure_runways, #landing_runways, #mixed_runways'
    );
    
    // Load preset if coming from presets page
    loadPresetIntoForm();
    
    console.log('Configuration form loaded successfully!');
});

// /**
//  * Validate that runway configuration adds up correctly
//  * @returns {boolean} True if valid, false otherwise
//  */
// function validateRunways() {
//     const departure = parseInt(document.getElementById('departure_runways').value) || 0;
//     const landing = parseInt(document.getElementById('landing_runways').value) || 0;
//     const mixed = parseInt(document.getElementById('mixed_runways').value) || 0;
    
//     const sum = departure + landing + mixed;
//     const errorElement = document.getElementById('runway-error');

//     // total_runways field is optional in current UI. If absent, require at least one runway.
//     const totalElement = document.getElementById('total_runways');
//     const total = totalElement ? (parseInt(totalElement.value) || 0) : sum;
    
//     if (sum <= 0 || sum !== total) {
//         if (errorElement) {
//             errorElement.style.display = 'block';
//             errorElement.classList.add('show');
//         }
//         return false;
//     } else {
//         if (errorElement) {
//             errorElement.style.display = 'none';
//             errorElement.classList.remove('show');
//         }
//         return true;
//     }
// }

/**
 * Start simulation - main form submission handler
 * @param {Event} event - Form submit event
 */
async function startSimulation(event) {
    event.preventDefault();
    
    // Show loading overlay
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.add('active');
    
    try {
        // Gather form data
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData);

        // Backend expects "runways" (total), not "total_runways" from form state.
        data.runways = String(
            (parseInt(data.departure_runways) || 0) +
            (parseInt(data.landing_runways) || 0) +
            (parseInt(data.mixed_runways) || 0)
        );
        
        // Add flag to save this config as a preset
        data.save_as_preset = true;
        
        console.log('Sending configuration:', data);
        
        // Call /start endpoint to create SimulationController
        const response = await fetch('/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        console.log('Start response:', result);
        
        if (result.success) {
            console.log('Simulation initialized successfully!');
            console.log('Redirecting to simulation screen...');
            
            setTimeout(() => {
                window.location.href = '/simulation-screen';
            }, 500);
        } else {
            loadingOverlay.classList.remove('active');
            
            const errorMsg = result.errors 
                ? result.errors.join('\n') 
                : 'Unknown error occurred';
            
            console.error('Error starting simulation:', errorMsg);
            alert('Error starting simulation:\n\n' + errorMsg);
        }
    } catch (error) {
        console.error('Network error:', error);
        loadingOverlay.classList.remove('active');
        
        alert(
            'Failed to start simulation. Please try again.\n\n' +
            'Error: ' + error.message + '\n\n' +
            'Make sure Flask server is running on the same port shown in your URL.'
        );
    }
}

/**
 * Navigate back to main menu
 */
function goBack() {
    console.log('Returning to main menu...');
    window.location.href = '/';
}

/**
 * Load preset data from sessionStorage and populate form
 */
function loadPresetIntoForm() {
    const presetConfigStr = sessionStorage.getItem('presetConfig');
    
    if (!presetConfigStr) {
        return;
    }
    
    try {
        const config = JSON.parse(presetConfigStr);
        
        console.log('Loading preset into form:', config);
        
        // Populate form fields
        const totalRunwaysEl = document.getElementById('total_runways');
        if (totalRunwaysEl) {
            totalRunwaysEl.value = config.runways;
        }
        document.getElementById('departure_runways').value = config.departure_runways;
        document.getElementById('landing_runways').value = config.landing_runways;
        document.getElementById('mixed_runways').value = config.mixed_runways;
        document.getElementById('inbound_flow').value = config.inbound_flow;
        document.getElementById('outbound_flow').value = config.outbound_flow;
        document.getElementById('cancellation_time').value = config.cancellation_time;
        document.getElementById('duration').value = config.duration;
        
        // Clear sessionStorage
        sessionStorage.removeItem('presetConfig');
        
        // Update header
        const header = document.querySelector('.header h1');
        if (header) {
            header.innerHTML = 'Configure Preset Simulation';
        }
        
        const subtitle = document.querySelector('.subtitle');
        if (subtitle) {
            subtitle.innerHTML = 'Loaded from saved preset - modify as needed';
        }
        
        console.log('Preset loaded successfully!');
        
    } catch (error) {
        console.error('Error loading preset:', error);
        sessionStorage.removeItem('presetConfig');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('configForm').dispatchEvent(new Event('submit'));
    }
    
    // Escape to go back
    if (e.key === 'Escape') {
        if (confirm('Return to main menu?')) {
            goBack();
        }
    }
});
