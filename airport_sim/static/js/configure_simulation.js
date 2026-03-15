/** Maximum total runways allowed across all types. */
const MAX_RUNWAYS = 10;

/** Initialize on page load. */
document.addEventListener('DOMContentLoaded', function() {
    // Add validation listeners
    const runwayInputs = document.querySelectorAll(
        '#departure_runways, #landing_runways, #mixed_runways'
    );

    runwayInputs.forEach(input => {
        input.addEventListener('input', enforceRunwayLimit);
    });

    // Load preset if coming from presets page
    loadPresetIntoForm();
    
    console.log('Configuration form loaded successfully!');
});

/**
 * Check total runways and show/hide an inline error message.
 */
function enforceRunwayLimit() {
    const dep = parseInt(document.getElementById('departure_runways').value) || 0;
    const lnd = parseInt(document.getElementById('landing_runways').value) || 0;
    const mix = parseInt(document.getElementById('mixed_runways').value) || 0;
    const total = dep + lnd + mix;

    // Get or create the error element
    let errorElement = document.getElementById('runway-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.id = 'runway-error';
        errorElement.style.color = '#e74c3c';
        errorElement.style.fontWeight = 'bold';
        errorElement.style.marginTop = '8px';
        errorElement.style.display = 'none';
        // Insert after the last runway input's parent
        const mixEl = document.getElementById('mixed_runways');
        mixEl.closest('.form-group, .field, div')?.after(errorElement)
            || mixEl.parentNode.appendChild(errorElement);
    }

    if (total > MAX_RUNWAYS) {
        errorElement.textContent = `Total runways is ${total} - cannot exceed ${MAX_RUNWAYS}. Please reduce your runway numbers.`;
        errorElement.style.display = 'block';
    } else {
        errorElement.style.display = 'none';
    }
}

/**
 * Validate form inputs and POST configuration to /start.
 * Redirects to the simulation screen on success.
 * @param {Event} event - Form submit event.
 */
async function startSimulation(event) {
    event.preventDefault();

    // Validate runway total before proceeding
    const dep = parseInt(document.getElementById('departure_runways').value) || 0;
    const lnd = parseInt(document.getElementById('landing_runways').value) || 0;
    const mix = parseInt(document.getElementById('mixed_runways').value) || 0;
    const totalRunways = dep + lnd + mix;

    if(dep < 0 || lnd < 0 || mix < 0) {
        alert('Runway numbers cannot be negative.');
        return;
    }   

    if (totalRunways <= 0) {
        alert('You need at least 1 runway to run the simulation.');
        return;
    }
    if (totalRunways > MAX_RUNWAYS) {
        alert(`Total runways cannot exceed ${MAX_RUNWAYS}. Currently: ${totalRunways}`);
        return;
    }

    // Show loading overlay
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.add('active');
    
    try {
        // Gather form data
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData);

        // Backend expects "runways" (total), not "total_runways" from form state.
        data.runways = String(totalRunways);
        
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

/** Navigate back to main menu. */
function goBack() {
    console.log('Returning to main menu...');
    window.location.href = '/';
}

/**
 * Load a preset configuration from sessionStorage and populate the form.
 * Clears the stored preset after loading.
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
        document.getElementById('health_emergency_p').value = config.health_emergency_prob;
        document.getElementById('mechanical_emergency_p').value = config.mechanical_emergency_prob;
        document.getElementById('fuel_emergency_p').value = config.fuel_emergency_prob;
        document.getElementById('medical_emergency_p').value = config.medical_emergency_prob;
        document.getElementById('weather_closure_prob').value = config.weather_closure_prob;
        document.getElementById('safety_closure_prob').value = config.safety_closure_prob;
        document.getElementById('construction_closure_prob').value = config.construction_closure_prob;
        document.getElementById('maintenance_closure_prob').value = config.maintenance_closure_prob;
        document.getElementById('runway_opening_prob').value = config.runway_opening_prob;
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

/** Keyboard shortcuts: Ctrl/Cmd+Enter to submit, Escape to go back. */
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