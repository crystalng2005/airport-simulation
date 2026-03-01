

// Start New Simulation
function startNewSimulation() {
    console.log("Starting new simulation...");

    window.location.href = '/simulation-screen';
}

// Load Preset
function loadPreset() {
    console.log("Loading preset...");
    // Redirect to presets page
    window.location.href = '/presets';
}

// View Results
function viewResults() {
    console.log("Viewing results...");
    window.location.href = '/results';
}

// Open Settings
function openSettings() {
    console.log("Opening settings...");
    // TO DO: Navigate to settings page or call Flask route
    alert("Settings\n\nThis will open the settings panel.");
    // window.location.href = '/settings';
}

// Exit Application
function exitApplication() {
    console.log("Exiting application...");
    const confirmExit = confirm("Are you sure you want to exit?");
    if (confirmExit) {
        alert("Thank you for using Airport Simulation System!");
        // window.close(); or redirect to goodbye page
    }
}

// Keyboard Navigation
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.menu-btn');
    
    // Add keyboard support
    buttons.forEach((button, index) => {
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                button.click();
            }
        });
    });
    
    console.log("Menu loaded successfully!");
});