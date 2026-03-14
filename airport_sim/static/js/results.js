/** Currently selected simulation IDs for comparison (max 2). */
let selectedSimulations = [];
/** All simulation results loaded from the backend. */
let allSimulations = [];
/** The simulation ID whose report is currently open. */
let currentReportId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadResults();
});

/* Fetch all simulation results from the backend and display them. */
async function loadResults() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('resultsContainer');
    const noResultsMessage = document.getElementById('noResultsMessage');

    try {
        // Get data from VisualisationController
        const response = await fetch('/api/get-all-results');
        const data = await response.json();
        
        loadingIndicator.style.display = 'none';

        if (!data.success || !data.results || data.results.length === 0) {
            noResultsMessage.style.display = 'block';
        } else {
            allSimulations = data.results; // Already limited to 50 by backend
            document.getElementById('totalCount').textContent = allSimulations.length;
            resultsContainer.style.display = 'block';
            displayResults(allSimulations);
        }
    } catch (error) {
        console.error('Error loading results:', error);
        loadingIndicator.style.display = 'none';
        noResultsMessage.style.display = 'block';
    }
}

/**
 * Render result rows into the results table.
 * @param {Object[]} results - Simulation result objects from the backend.
 */
function displayResults(results) {
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = '';

    // Backend already sorted by most recent
    results.forEach((result) => {
        const row = createResultRow(result);
        tbody.appendChild(row);
    });
}

/**
 * Create a table row element for a single simulation result.
 * @param {Object} result - A simulation result containing report and config data.
 * @returns {HTMLTableRowElement} The constructed row.
 */
function createResultRow(result) {
    const row = document.createElement('tr');
    row.dataset.simId = result.id;

    // Format date for display
    const date = new Date(result.completed_at);
    const formattedDate = date.toLocaleDateString('en-GB', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
    const formattedTime = date.toLocaleTimeString('en-GB', {
        hour: '2-digit',
        minute: '2-digit'
    });

    const report = result.report;
    const config = result.config;

    row.innerHTML = `
        <td>
            <input type="checkbox" class="select-checkbox" 
                   onchange="toggleSelection('${result.id}')" 
                   id="checkbox-${result.id}">
        </td>
        <td class="number">#${result.id}</td>
        <td>
            <div>${formattedDate}</div>
            <div style="font-size: 0.8rem; color: #64748b;">${formattedTime}</div>
        </td>
        <td>${result.duration}</td>
        <td class="number">${config.total_runways}</td>
        <td class="number">${report.total_planes}</td>
        <td class="${report.diversions > 0 ? 'highlight' : 'number'}">${report.diversions}</td>
        <td class="${report.cancellations > 0 ? 'highlight' : 'number'}">${report.cancellations}</td>
        <td class="number">${report.queue_max}</td>
        <td>
            <button class="btn btn-view" onclick="viewReport('${result.id}')">
                View
            </button>
            <button class="btn btn-export" onclick="exportReport('${result.id}')">
                Export
            </button>
        </td>
    `;

    return row;
}

/**
 * Toggle a simulation's selection state for comparison (max 2).
 * @param {string} simId - The simulation ID to toggle.
 */
function toggleSelection(simId) {
    const checkbox = document.getElementById(`checkbox-${simId}`);
    const row = document.querySelector(`tr[data-sim-id="${simId}"]`);
    
    if (checkbox.checked) {
        if (selectedSimulations.length < 2) {
            selectedSimulations.push(simId);
            row.classList.add('selected');
        } else {
            checkbox.checked = false;
            alert('You can only select 2 simulations for comparison');
        }
    } else {
        selectedSimulations = selectedSimulations.filter(id => id !== simId);
        row.classList.remove('selected');
    }

    updateCompareButton();
}

/** Update the compare button label and disabled state based on selection count. */
function updateCompareButton() {
    const compareBtn = document.getElementById('compareBtn');
    const count = selectedSimulations.length;
    
    compareBtn.textContent = `Compare Selected (${count}/2)`;
    compareBtn.disabled = count !== 2;
}

/** Deselect all simulations and reset the compare button. */
function clearSelection() {
    selectedSimulations.forEach(simId => {
        const checkbox = document.getElementById(`checkbox-${simId}`);
        const row = document.querySelector(`tr[data-sim-id="${simId}"]`);
        if (checkbox) checkbox.checked = false;
        if (row) row.classList.remove('selected');
    });
    
    selectedSimulations = [];
    updateCompareButton();
}

/** POST the two selected simulation IDs to the backend and display the comparison modal. */
async function compareSelected() {
    if (selectedSimulations.length !== 2) {
        alert('Please select exactly 2 simulations to compare');
        return;
    }

    try {
        // Get comparison data from VisualisationController
        // Backend calculates speedup, reduction, improvements
        const response = await fetch('/api/compare-simulations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sim_id_1: selectedSimulations[0],
                sim_id_2: selectedSimulations[1]
            })
        });

        const data = await response.json();

        if (data.success) {
            // Just display the pre-calculated data
            showComparisonModal(data.comparison);
            loadComparisonPlots(selectedSimulations[0], selectedSimulations[1]);
        } else {
            alert('Error comparing simulations: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to compare simulations');
    }
}

/**
 * Populate and display the comparison modal with backend-calculated metrics.
 * @param {Object} comparison - Comparison data containing both simulations and metrics.
 */
function showComparisonModal(comparison) {
    const modal = document.getElementById('comparisonModal');
    const content = document.getElementById('comparisonContent');

    const sim1 = comparison.simulation_1;
    const sim2 = comparison.simulation_2;
    const metrics = comparison.metrics; // ALL calculated by backend

    content.innerHTML = `
        <!-- Simulation Info -->
        <div class="comparison-header">
            <div class="sim-info">
                <h3>Simulation #${sim1.id}</h3>
                <p><strong>Date:</strong> ${new Date(sim1.completed_at).toLocaleDateString('en-GB')}</p>
                <p><strong>Runways:</strong> ${sim1.config.total_runways} 
                   (L:${sim1.config.landing_runways}, D:${sim1.config.departure_runways}, M:${sim1.config.mixed_runways})</p>
                <p><strong>Efficiency:</strong> ${sim1.report.efficiency}%</p>
            </div>
            <div class="sim-info">
                <h3>Simulation #${sim2.id}</h3>
                <p><strong>Date:</strong> ${new Date(sim2.completed_at).toLocaleDateString('en-GB')}</p>
                <p><strong>Runways:</strong> ${sim2.config.total_runways} 
                   (L:${sim2.config.landing_runways}, D:${sim2.config.departure_runways}, M:${sim2.config.mixed_runways})</p>
                <p><strong>Efficiency:</strong> ${sim2.report.efficiency}%</p>
            </div>
        </div>

        <!-- Performance Metrics - ALL from backend -->
        <div style="margin-bottom: 30px;">
            <h3 style="color: #1e3a8a; margin-bottom: 15px;">Performance Comparison</h3>
            <div class="metric-cards">
                <div class="metric-card">
                    <div class="metric-label">Diversion Change</div>
                    <div class="metric-value ${metrics.diversions.is_improvement ? 'better' : 'worse'}">
                        ${metrics.diversions.text}
                    </div>
                    <div class="metric-change">${sim1.report.diversions} → ${sim2.report.diversions}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Cancellation Change</div>
                    <div class="metric-value ${metrics.cancellations.is_improvement ? 'better' : 'worse'}">
                        ${metrics.cancellations.text}
                    </div>
                    <div class="metric-change">${sim1.report.cancellations} → ${sim2.report.cancellations}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Queue Size Change</div>
                    <div class="metric-value ${metrics.queue_max.is_improvement ? 'better' : 'worse'}">
                        ${metrics.queue_max.text}
                    </div>
                    <div class="metric-change">${sim1.report.queue_max} → ${sim2.report.queue_max}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Efficiency Change</div>
                    <div class="metric-value ${metrics.efficiency.is_improvement ? 'better' : 'worse'}">
                        ${metrics.efficiency.text}
                    </div>
                    <div class="metric-change">${metrics.efficiency.sim1_value}% → ${metrics.efficiency.sim2_value}%</div>
                </div>
            </div>
        </div>

        <!-- Detailed Table -->
        <div>
            <h3 style="color: #1e3a8a; margin-bottom: 15px;">Detailed Metrics</h3>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Simulation #${sim1.id}</th>
                        <th>Simulation #${sim2.id}</th>
                        <th>Change</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Total Planes</strong></td>
                        <td>${sim1.report.total_planes}</td>
                        <td>${sim2.report.total_planes}</td>
                        <td class="neutral">${sim2.report.total_planes - sim1.report.total_planes}</td>
                    </tr>
                    <tr>
                        <td><strong>Diversions</strong></td>
                        <td class="${sim1.report.diversions < sim2.report.diversions ? 'better' : ''}">${sim1.report.diversions}</td>
                        <td class="${sim2.report.diversions < sim1.report.diversions ? 'better' : ''}">${sim2.report.diversions}</td>
                        <td class="${metrics.diversions.is_improvement ? 'better' : 'worse'}">${metrics.diversions.text}</td>
                    </tr>
                    <tr>
                        <td><strong>Cancellations</strong></td>
                        <td class="${sim1.report.cancellations < sim2.report.cancellations ? 'better' : ''}">${sim1.report.cancellations}</td>
                        <td class="${sim2.report.cancellations < sim1.report.cancellations ? 'better' : ''}">${sim2.report.cancellations}</td>
                        <td class="${metrics.cancellations.is_improvement ? 'better' : 'worse'}">${metrics.cancellations.text}</td>
                    </tr>
                    <tr>
                        <td><strong>Max Queue Size</strong></td>
                        <td>${sim1.report.queue_max}</td>
                        <td>${sim2.report.queue_max}</td>
                        <td class="${metrics.queue_max.is_improvement ? 'better' : 'worse'}">${metrics.queue_max.text}</td>
                    </tr>
                    <tr>
                        <td><strong>Max Holding Pattern</strong></td>
                        <td>${sim1.report.holding_max}</td>
                        <td>${sim2.report.holding_max}</td>
                        <td class="${metrics.holding_max.is_improvement ? 'better' : 'worse'}">${metrics.holding_max.text}</td>
                    </tr>
                    <tr>
                        <td><strong>Total Fuel Used</strong></td>
                        <td>${sim1.report.tot_fuel_used.toFixed(1)}</td>
                        <td>${sim2.report.tot_fuel_used.toFixed(1)}</td>
                        <td class="${metrics.fuel_used.is_improvement ? 'better' : 'worse'}">${metrics.fuel_used.text}</td>
                    </tr>
                    <tr>
                        <td><strong>Efficiency</strong></td>
                        <td>${sim1.report.efficiency}%</td>
                        <td>${sim2.report.efficiency}%</td>
                        <td class="${metrics.efficiency.is_improvement ? 'better' : 'worse'}">${metrics.efficiency.text}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;

    showComparisonResults();
    modal.style.display = 'flex';
}

/** Switch the comparison modal to the results tab. */
function showComparisonResults() {
    const content = document.getElementById('comparisonContent');
    const plotsSection = document.getElementById('comparisonPlotsSection');
    const resultsBtn = document.getElementById('comparisonResultsBtn');
    const plotsBtn = document.getElementById('comparisonPlotsBtn');

    if (content) content.style.display = 'block';
    if (plotsSection) plotsSection.style.display = 'none';
    if (resultsBtn) {
        resultsBtn.classList.remove('btn-secondary');
        resultsBtn.classList.add('btn-primary');
    }
    if (plotsBtn) {
        plotsBtn.classList.remove('btn-primary');
        plotsBtn.classList.add('btn-secondary');
    }
}

/** Switch the comparison modal to the plots tab. */
function showComparisonPlots() {
    const content = document.getElementById('comparisonContent');
    const plotsSection = document.getElementById('comparisonPlotsSection');
    const resultsBtn = document.getElementById('comparisonResultsBtn');
    const plotsBtn = document.getElementById('comparisonPlotsBtn');

    if (content) content.style.display = 'none';
    if (plotsSection) plotsSection.style.display = 'block';
    if (resultsBtn) {
        resultsBtn.classList.remove('btn-primary');
        resultsBtn.classList.add('btn-secondary');
    }
    if (plotsBtn) {
        plotsBtn.classList.remove('btn-secondary');
        plotsBtn.classList.add('btn-primary');
    }
}

/**
 * Fetch the full report for a simulation and display it in the report modal.
 * @param {string} simId - The simulation ID to view.
 */
async function viewReport(simId) {
    currentReportId = simId;
    
    try {
        // Get full report from VisualisationController
        const response = await fetch(`/api/get-full-report/${simId}`);
        const data = await response.json();

        if (data.success === false) {
            alert('Error loading report: ' + (data.error || 'Unknown error'));
            return;
        }

        const report = data.report || (data.success ? data.report : null);
        if (!report) {
            alert('Error loading report: Report data missing');
            return;
        }

        // Display report and matching plots for this specific simulation
        showReportModal(report, simId);
        await loadSavedReportPlots(simId);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load report');
    }
}

/**
 * Populate and display the report modal with simulation metrics.
 * @param {Object} report - Report data from the backend.
 * @param {string|null} [simId=null] - Optional simulation ID for the heading.
 */
function showReportModal(report, simId = null) {
    const modal = document.getElementById('reportModal');
    const content = document.getElementById('reportContent');
    const displayId = simId !== null ? simId : (report.id ?? 'N/A');

    // Backend already calculated everything
    content.innerHTML = `
        <h3 style="color: #1e3a8a; margin-bottom: 20px;">Simulation #${displayId} - Full Report</h3>
        
        <div class="metric-cards">
            <div class="metric-card">
                <div class="metric-label">Total Planes</div>
                <div class="metric-value">${report.total_planes}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Diversions</div>
                <div class="metric-value" style="color: #ef4444;">${report.diversions}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cancellations</div>
                <div class="metric-value" style="color: #ef4444;">${report.cancellations}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Efficiency</div>
                <div class="metric-value" style="color: #10b981;">${report.efficiency}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Max Queue Size</div>
                <div class="metric-value">${report.queue_max}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Max Holding Pattern</div>
                <div class="metric-value">${report.holding_max}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Fuel Used</div>
                <div class="metric-value">${report.tot_fuel_used.toFixed(1)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Wait Time</div>
                <div class="metric-value">${report.avg_wait_time} min</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Fuel/Plane</div>
                <div class="metric-value">${report.avg_fuel_per_plane}</div>
            </div>
        </div>
    `;

    showReportResults();
    modal.style.display = 'flex';
}

/** Switch the report modal to the results tab. */
function showReportResults() {
    const content = document.getElementById('reportContent');
    const plotsSection = document.getElementById('reportPlotsSection');
    const resultsBtn = document.getElementById('reportResultsBtn');
    const plotsBtn = document.getElementById('reportPlotsBtn');

    if (content) content.style.display = 'block';
    if (plotsSection) plotsSection.style.display = 'none';
    if (resultsBtn) {
        resultsBtn.classList.remove('btn-secondary');
        resultsBtn.classList.add('btn-primary');
    }
    if (plotsBtn) {
        plotsBtn.classList.remove('btn-primary');
        plotsBtn.classList.add('btn-secondary');
    }
}

/** Switch the report modal to the plots tab. */
function showReportPlots() {
    const content = document.getElementById('reportContent');
    const plotsSection = document.getElementById('reportPlotsSection');
    const resultsBtn = document.getElementById('reportResultsBtn');
    const plotsBtn = document.getElementById('reportPlotsBtn');

    if (content) content.style.display = 'none';
    if (plotsSection) plotsSection.style.display = 'block';
    if (resultsBtn) {
        resultsBtn.classList.remove('btn-primary');
        resultsBtn.classList.add('btn-secondary');
    }
    if (plotsBtn) {
        plotsBtn.classList.remove('btn-secondary');
        plotsBtn.classList.add('btn-primary');
    }
}

/**
 * Fetch and display saved plot images for a simulation report.
 * @param {string} simId - The simulation ID to load plots for.
 */
async function loadSavedReportPlots(simId) {
    try {
        const response = await fetch(`/api/report-plots/${simId}`);
        const data = await response.json();

        const plotsContainer = document.getElementById('reportPlotsContainer');
        if (!plotsContainer) return;
        plotsContainer.innerHTML = '';

        if (!data.success || !data.plots || Object.keys(data.plots).length === 0) {
            plotsContainer.innerHTML = '<p style="color:#64748b;">No plots available for this simulation.</p>';
            return;
        }

        const plotLabels = {
            wait_times: 'Wait Times',
            hold_times: 'Hold Times',
            takeoff_delays: 'Take-off Delays',
            arrival_delays: 'Arrival Delays',
            outcome_summary: 'Outcome Summary',
            operations_snapshot: 'Operations Snapshot'
        };

        for (const [key, base64] of Object.entries(data.plots)) {
            const wrapper = document.createElement('div');
            wrapper.style.textAlign = 'center';

            const label = document.createElement('div');
            label.textContent = plotLabels[key] || key;
            label.style.fontWeight = 'bold';
            label.style.marginBottom = '4px';
            label.style.color = '#1e3a8a';
            label.style.fontSize = '0.85rem';

            const img = document.createElement('img');
            img.src = 'data:image/png;base64,' + base64;
            img.alt = plotLabels[key] || key;
            img.style.width = '100%';
            img.style.borderRadius = '6px';
            img.style.border = '1px solid #e2e8f0';

            wrapper.appendChild(label);
            wrapper.appendChild(img);
            plotsContainer.appendChild(wrapper);
        }
    } catch (error) {
        console.error('Error loading report plots:', error);
    }
}

/** Export the currently viewed report. */
function exportCurrentReport() {
    if (currentReportId) {
        exportReport(currentReportId);
    }
}

/**
 * Trigger a report export download via the backend.
 * @param {string} simId - The simulation ID to export.
 */
function exportReport(simId) {
    window.location.href = `/api/export-report/${simId}`;
    setTimeout(() => {
        alert('Report exported successfully!');
    }, 500);
}

/** Close the comparison modal and clear its plots. */
function closeComparison() {
    document.getElementById('comparisonModal').style.display = 'none';
    // Clear plots when closing
    const plotsSection = document.getElementById('comparisonPlotsSection');
    const plotsContainer = document.getElementById('comparisonPlotsContainer');
    if (plotsSection) plotsSection.style.display = 'none';
    if (plotsContainer) plotsContainer.innerHTML = '';
    showComparisonResults();
}

/**
 * Fetch and display side-by-side comparison plot images.
 * @param {string} simId1 - First simulation ID.
 * @param {string} simId2 - Second simulation ID.
 */
async function loadComparisonPlots(simId1, simId2) {
    try {
        const response = await fetch('/api/comparison-plots', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sim_id_1: simId1, sim_id_2: simId2 })
        });
        const data = await response.json();

        if (!data.success || !data.plots) {
            console.log('No comparison plots available');
            return;
        }

        const plotsSection = document.getElementById('comparisonPlotsSection');
        const plotsContainer = document.getElementById('comparisonPlotsContainer');
        plotsContainer.innerHTML = '';

        const plotLabels = {
            key_counts: 'Planes, Diversions & Cancellations',
            queues: 'Queue & Holding',
            times: 'Average Times',
            fuel_efficiency: 'Fuel & Efficiency'
        };

        for (const [key, base64] of Object.entries(data.plots)) {
            const wrapper = document.createElement('div');
            wrapper.style.textAlign = 'center';

            const label = document.createElement('div');
            label.textContent = plotLabels[key] || key;
            label.style.fontWeight = 'bold';
            label.style.marginBottom = '4px';
            label.style.color = '#1e3a8a';
            label.style.fontSize = '0.85rem';

            const img = document.createElement('img');
            img.src = 'data:image/png;base64,' + base64;
            img.alt = plotLabels[key] || key;
            img.style.width = '100%';
            img.style.borderRadius = '6px';
            img.style.border = '1px solid #e2e8f0';

            wrapper.appendChild(label);
            wrapper.appendChild(img);
            plotsContainer.appendChild(wrapper);
        }

    } catch (error) {
        console.error('Error loading comparison plots:', error);
    }
}

/** Close the report modal and clear its plots. */
function closeReport() {
    document.getElementById('reportModal').style.display = 'none';
    currentReportId = null;
    const plotsContainer = document.getElementById('reportPlotsContainer');
    if (plotsContainer) plotsContainer.innerHTML = '';
    showReportResults();
}

/** Navigate back to main menu. */
function goToMenu() {
    window.location.href = '/';
}

// Close modals when clicking outside
window.onclick = function(event) {
    const compModal = document.getElementById('comparisonModal');
    const repModal = document.getElementById('reportModal');
    
    if (event.target === compModal) {
        closeComparison();
    }
    if (event.target === repModal) {
        closeReport();
    }
}