let selectedSimulations = [];
let currentReportId = null;

document.addEventListener('DOMContentLoaded', async function() {
    const report = await getReport();
    showReportModal(report);
});

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

function showReport(report){
  if (!report) return;

  // For Turki to change
  const reportBox = document.querySelector('.report-container');
  if (!reportBox) {
    console.log('Final report:', report);
    return;
  }

  reportBox.innerHTML = `
    <h3>Simulation Report</h3>
    <p>Total planes: ${report.total_planes}</p>
    <p>Diversions: ${report.diversions}</p>
    <p>Cancellations: ${report.cancellations}</p>
    <p>Efficiency: ${report.efficiency}</p>
    <p>Avg wait: ${report.avg_wait_time}</p>
    <p>Max hold: ${report.max_hold_time}</p>
  `;
}


// Load all simulation results from backend
// Backend returns ALL calculated data
async function loadResults() {
    const resultsContainer = document.getElementById('resultsContainer');

    try {
        // Get data from VisualisationController
        const response = await fetch('/api/get-all-results');
        const data = await response.json();
        
        loadingIndicator.style.display = 'none';

        if (!data.success || !data.results || data.results.length === 0) {
            noResultsMessage.style.display = 'block';
        } else {
            // document.getElementById('totalCount').textContent = allSimulations.length;
            resultsContainer.style.display = 'block';
            displayResults(data.results);
        }
    } catch (error) {
        console.error('Error loading results:', error);
        loadingIndicator.style.display = 'none';
        noResultsMessage.style.display = 'block';
    }
}

// Display results in table - just rendering
function displayResults(result) {
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = '';

    const row = createResultRow(result);
    tbody.appendChild(row);
}

// Create table row - just display data from backend
function createResultRow(result) {
    const row = document.createElement('tr');
    // row.dataset.simId = result.id;

    // Format date for display
    // const date = new Date(result.completed_at);
    // const formattedDate = date.toLocaleDateString('en-GB', {
    //     year: 'numeric',
    //     month: 'short',
    //     day: 'numeric'
    // });
    // const formattedTime = date.toLocaleTimeString('en-GB', {
    //     hour: '2-digit',
    //     minute: '2-digit'
    // });

    const report = result.report;
    const config = result.config;

    row.innerHTML = `
        <td>
            <input type="checkbox" class="select-checkbox" 
        </td>
        <td>
            <div>${formattedDate}</div>
            <div style="font-size: 0.8rem; color: #64748b;">${formattedTime}</div>
        </td>
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

// Toggle simulation selection
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

// Update compare button
function updateCompareButton() {
    const compareBtn = document.getElementById('compareBtn');
    const count = selectedSimulations.length;
    
    compareBtn.textContent = `Compare Selected (${count}/2)`;
    compareBtn.disabled = count !== 2;
}

// Clear selection
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


// Compare selected simulations
// Backend does ALL calculations
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

// Show comparison modal - just display backend data
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

// View full report - backend provides all data
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

// Show report modal - just display backend data
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

// Export current report
function exportCurrentReport() {
    window.location.href = '/api/export-current-report';
}

// Export report - backend handles file generation
function exportReport(simId) {
    window.location.href = `/api/export-report/${simId}`;
}


// Close modals
 
function closeComparison() {
    document.getElementById('comparisonModal').style.display = 'none';
}

function closeReport() {
    document.getElementById('reportModal').style.display = 'none';
    currentReportId = null;
}

// Go to menu
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



/*
document.addEventListener("DOMContentLoaded", () => {
    const simId = getSimulationId();
    loadSimulation(simId);
});

function getSimulationId() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}

async function loadSimulation(simId) {

    const loading = document.getElementById("loadingIndicator");
    const content = document.getElementById("resultContent");

    try {

        const response = await fetch(`/api/get-full-report/${simId}`);
        const data = await response.json();

        loading.style.display = "none";

        if (!data.success) {
            content.innerHTML = "<p>Failed to load simulation</p>";
            content.style.display = "block";
            return;
        }

        const report = data.report;

        content.innerHTML = `
        <h2>Simulation #${report.id}</h2>

        <div class="metric-cards">

            <div class="metric-card">
                <div class="metric-label">Total Planes</div>
                <div class="metric-value">${report.total_planes}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Diversions</div>
                <div class="metric-value">${report.diversions}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Cancellations</div>
                <div class="metric-value">${report.cancellations}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Efficiency</div>
                <div class="metric-value">${report.efficiency}%</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Max Queue</div>
                <div class="metric-value">${report.queue_max}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Fuel Used</div>
                <div class="metric-value">${report.tot_fuel_used.toFixed(1)}</div>
            </div>

        </div>
        `;

        content.style.display = "block";

    } catch (error) {
        console.error(error);
    }
}
*/