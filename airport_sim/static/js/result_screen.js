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

/** Navigate back to the main menu. */
function goToMenu() {
    window.location.href = '/';
}