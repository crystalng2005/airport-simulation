/** Navigate to the simulation configuration page. */
function startNewSimulation() {
    window.location.href = '/configure-simulation';  // Changed!
}

/** Navigate to the presets page. */
function loadPreset() {
    console.log("Loading preset...");
    // Redirect to presets page
    window.location.href = '/presets';
}

/** Navigate to the results page. */
function viewResults() {
    console.log("Viewing results...");
    window.location.href = '/results';
}


/** Confirm and handle application exit action. */
function exitApplication() {
    console.log("Exiting application...");
    const confirmExit = confirm("Are you sure you want to exit?");
    if (confirmExit) {
        alert("Thank you for using Airport Simulation System!");
        // window.close(); or redirect to goodbye page
    }
}

/** Add keyboard navigation support for menu buttons. */
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