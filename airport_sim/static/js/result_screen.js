let selectedSimulations = [];
let currentReportId = null;

/** Load report data and plots when the page is ready. */
document.addEventListener('DOMContentLoaded', async function() {
    const report = await getReport();
    showReportModal(report);
    await loadPlots();
});

/**
 * Obtain the report statistics from the backend.
 * @returns {Promise<Object|null>} Report data, or null on failure.
 */
async function getReport(){
  try {
    const response = await fetch('/api/report');
    const data = await response.json();

    if (!data.success) {
      console.error('Failed to get report:', data.errors || data.error);
      return null;
    }

    return data.report;
  } catch (error) {
    console.error('Error fetching report:', error);
    return null;
  }
}

/**
 * Show the report modal using backend-provided data.
 * @param {Object} report - Report metrics object.
 * @returns {void}
 */
function showReportModal(report) {
    const modal = document.getElementById('reportModal');
    const content = document.getElementById('reportContent');

    // Backend already calculated everything
    content.innerHTML = 

        // `<h3 style="color: #1e3a8a; margin-bottom: 20px;">Simulation #${report.id} - Full Report</h3>`+
        `
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
                <div class="metric-value">${report.avg_wait_time.toFixed(1)} min</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Fuel/Plane</div>
                <div class="metric-value">${report.avg_fuel_per_plane.toFixed(1)}</div>
            </div>
        </div>
    `;

    showReportResults();
    modal.style.display = 'flex';
}

/**
 * Display report statistics and activate the results tab.
 * @returns {void}
 */
function showReportResults() {
    const reportContent = document.getElementById('reportContent');
    const plotsSection = document.getElementById('plotsSection');
    const resultsBtn = document.getElementById('reportResultsBtn');
    const plotsBtn = document.getElementById('reportPlotsBtn');

    if (reportContent) reportContent.style.display = 'block';
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

/**
 * Compare two selected simulations using backend-calculated metrics.
 * @returns {Promise<void>}
 */
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
        } else {
            alert('Error comparing simulations: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to compare simulations');
    }
}

/**
 * Show the comparison modal with backend-provided comparison data.
 * @param {Object} comparison - Comparison payload from backend.
 * @returns {void}
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

    modal.style.display = 'flex';
}

/**
 * View the full report for a selected simulation.
 * @param {number|string} simId - Selected simulation ID.
 * @returns {Promise<void>}
 */
async function viewReport(simId) {
    currentReportId = simId;
    
    try {
        // Get full report from VisualisationController
        const response = await fetch(`/api/get-full-report/${simId}`);
        const data = await response.json();

        if (data.success) {
            // Just display the data
            showReportModal(data.report);
        } else {
            alert('Error loading report: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load report');
    }
}

/**
 * Display report plots and activate the plots tab.
 * @returns {void}
 */
function showReportPlots() {
    const reportContent = document.getElementById('reportContent');
    const plotsSection = document.getElementById('plotsSection');
    const resultsBtn = document.getElementById('reportResultsBtn');
    const plotsBtn = document.getElementById('reportPlotsBtn');

    if (reportContent) reportContent.style.display = 'none';
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

/** Export the current report from the backend. */
function exportCurrentReport() {
    window.location.href = '/api/export-current-report';
}

/**
 * Load and display performance plots from the backend.
 * @returns {Promise<void>}
 */
async function loadPlots() {
    try {
        const response = await fetch('/api/report-plots');
        const data = await response.json();

        if (!data.success || !data.plots || Object.keys(data.plots).length === 0) {
            console.log('No plots available');
            return;
        }

        const plotsSection = document.getElementById('plotsSection');
        const plotsContainer = document.getElementById('plotsContainer');
        plotsContainer.innerHTML = '';

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
            label.style.fontSize = '0.8rem';

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

        plotsSection.style.overflow = 'auto';
    } catch (error) {
        console.error('Error loading plots:', error);
    }
}

/** Close the comparison modal. */
function closeComparison() {
    document.getElementById('comparisonModal').style.display = 'none';
}

/** Navigate back to the main menu. */
function goToMenu() {
    window.location.href = '/';
}