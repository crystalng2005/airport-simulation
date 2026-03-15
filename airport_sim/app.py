"""Flask entrypoint and route registration for the airport simulator."""

import os
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file, session
from flask.typing import ResponseReturnValue

import logic.globals.reportData as RD
from logic.report import PerformanceReport
from logic.visualisation import VisualisationController

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
)

class MainController:
    """Container for shared controller instances used by route handlers."""

    def __init__(self) -> None:
        self.visualisation_controller = VisualisationController()


controller = MainController()


# -------------------------------
# Shared route helpers
# -------------------------------

def _no_active_simulation_error() -> ResponseReturnValue:
    """Return a standard 400 response when no simulation is active."""
    return jsonify({'success': False, 'error': 'No active simulation'}), 400

def _require_active_simulation() -> ResponseReturnValue | None:
    """Validate that a simulation exists, returning an error response if not."""
    if not controller.visualisation_controller.hasSimulation():
        return _no_active_simulation_error()
    return None

def _read_json_body() -> dict[str, Any] | None:
    """Parse and return a JSON object payload, or None when invalid."""
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        return data
    return None

def _success(status_code: int = 200, **payload: Any) -> ResponseReturnValue:
    """Build a standardised success JSON response envelope."""
    return jsonify({'success': True, **payload}), status_code

def _error(message: str, status_code: int = 400, **payload: Any) -> ResponseReturnValue:
    """Build a standardised error JSON response envelope."""
    return jsonify({'success': False, 'error': message, **payload}), status_code

# -------------------------------
# Page routes
# -------------------------------

@app.route('/')
def index() -> str:
    """Render the application landing page."""
    return render_template('menu.html')

@app.route('/simulation-screen')
def simulation_page() -> str:
    """Render the live simulation screen."""
    return render_template('simulation_screen.html')

@app.route('/configure-simulation')
def configure_simulation_page() -> str:
    """Render the simulation configuration page."""
    return render_template('configure_simulation.html')

@app.route('/results')
def results_page() -> str:
    """Render the results summary page."""
    return render_template('results.html')

@app.route('/result-screen')
def result_screen_page() -> str:
    """Render the detailed single-result screen."""
    return render_template('result_screen.html')

@app.route('/presets')
def presets_page() -> str:
    """Render the presets management page."""
    return render_template('presets.html')


# -------------------------------
# Simulation API
# -------------------------------

@app.route('/start', methods=['POST'])
def start_sim() -> ResponseReturnValue:
    """Start a new simulation from JSON configuration payload."""
    data = _read_json_body()
    if data is None:
        return _error('Invalid JSON body', 400)

    try:
        controller.visualisation_controller.startSimulation(data)
        return _success(200, message='Simulation started')
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

@app.route('/api/next-frame', methods=['POST'])
def next_frame() -> ResponseReturnValue:
    """Advance the active simulation by one frame/tick."""
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    controller.visualisation_controller.tick()
    return _success(200, message='Frame advanced')

@app.route('/api/simulation-finished', methods=['GET'])
def is_simulation_finished() -> ResponseReturnValue:
    """Return whether the current simulation has completed."""
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    return _success(
        200,
        finished=controller.visualisation_controller.isSimulationFinished(),
    )

@app.route('/api/current-frame-actions', methods=['GET'])
def get_current_frame_actions() -> ResponseReturnValue:
    """Return actions recorded for the current simulation frame."""
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    actions = controller.visualisation_controller.getCurrentFrameActions()
    return _success(200, actions=actions)

@app.route('/api/current-time', methods=['GET'])
def get_current_time() -> ResponseReturnValue:
    """Return the current simulation clock time."""
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    return _success(200, time=controller.visualisation_controller.getCurrentTime())

@app.route('/api/aircraft/<plane_call_sign>', methods=['GET'])
def get_aircraft(plane_call_sign: str) -> ResponseReturnValue:
    """Return aircraft details for a given call sign."""
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    aircraft = controller.visualisation_controller.getAircraftByCallSign(plane_call_sign)
    if not aircraft:
        return _error('Aircraft not found', 404)

    return _success(200, aircraft=aircraft.return_data())

@app.route('/api/number-of-runways', methods=['GET'])
def get_number_of_runways() -> ResponseReturnValue:
    """Return the configured number of runways for the active simulation."""
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    return _success(200, number=controller.visualisation_controller.getNumberOfRunways())

@app.route('/api/runway-statuses', methods=['GET'])
def get_runway_status() -> ResponseReturnValue:
    """Return current availability/operational runway statuses."""
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    return _success(**{'status': controller.visualisation_controller.getRunwayStatuses()})

@app.route('/api/runway-modes', methods=['GET'])
def get_runway_modes() -> ResponseReturnValue:
    """Return mode configuration for each runway."""
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    return _success(200, mode=controller.visualisation_controller.getRunwayModes())

@app.route('/api/report', methods=['GET'])
def get_report() -> ResponseReturnValue:
    """Return the current in-memory simulation report when available."""
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    report = controller.visualisation_controller.getCurrentSimulationReport()
    if report is None:
        return _error('Report not ready', 404)

    return _success(200, report=report)

# -------------------------------
# Preset API
# -------------------------------

@app.route('/api/get-preset-data/<int:preset_id>', methods=['GET'])
def get_preset_data(preset_id: int) -> ResponseReturnValue:
    """Fetch saved preset configuration and related report data by preset ID."""
    try:
        preset_data = controller.visualisation_controller.getPresetData(preset_id)

        if preset_data:
            return _success(
                200,
                vars=preset_data.get('vars', {}),
                planes=preset_data.get('planes', []),
                report=preset_data.get('report', {}),
            )

        return _error('Preset not found', 404)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

@app.route('/api/get-presets', methods=['GET'])
def get_presets() -> ResponseReturnValue:
    """Return metadata for all available simulation presets."""
    try:
        presets = controller.visualisation_controller.getAvailablePresets()
        return _success(200, presets=presets)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

@app.route('/api/load-preset', methods=['POST'])
def load_preset() -> ResponseReturnValue:
    """Load a preset into session state for subsequent simulation startup."""
    data = _read_json_body()
    if data is None:
        return _error('Invalid JSON body', 400)

    preset_id = data.get('preset_id')
    if preset_id is None:
        return _error('No preset_id provided', 400)

    try:
        preset_data = controller.visualisation_controller.getPresetData(preset_id)
        if preset_data and 'vars' in preset_data:
            session['preset_mode'] = True
            session['preset_id'] = preset_id

            return _success(200, message='Preset loaded successfully')

        return _error('Preset not found', 404)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

# -------------------------------
# Results and comparison API
# -------------------------------

@app.route('/api/get-all-results', methods=['GET'])
def get_all_results() -> ResponseReturnValue:
    """Return summary entries for all saved simulation results."""
    try:
        results = controller.visualisation_controller.getAllSimulationResults()
        return _success(200, results=results)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

@app.route('/api/get-full-report/<int:sim_id>', methods=['GET'])
def get_full_report(sim_id: int) -> ResponseReturnValue:
    """Return the full saved report payload for a simulation ID."""
    try:
        report = controller.visualisation_controller.getSimulationReport(sim_id)
        if report is None:
            return _error('Simulation report not found', 404)

        return _success(200, report=report.get('report', {}))
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

@app.route('/api/compare-simulations', methods=['POST'])
def compare_simulations() -> ResponseReturnValue:
    """Compare two saved simulations and return derived comparison metrics."""
    data = _read_json_body()
    if data is None:
        return _error('Invalid JSON body', 400)

    sim_id_1 = data.get('sim_id_1')
    sim_id_2 = data.get('sim_id_2')

    if sim_id_1 is None or sim_id_2 is None:
        return _error('Missing simulation IDs', 400)

    try:
        comparison = controller.visualisation_controller.compareSimulations(int(sim_id_1), int(sim_id_2))
        if comparison is None:
            return _error('One or both simulation IDs not found', 404)

        return _success(200, comparison=comparison)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

@app.route('/api/comparison-plots', methods=['POST'])
def comparison_plots() -> ResponseReturnValue:
    """Generate side-by-side bar chart plots comparing two simulation reports."""
    data = _read_json_body()
    if data is None:
        return _error('Invalid JSON body', 400)

    sim_id_1 = data.get('sim_id_1')
    sim_id_2 = data.get('sim_id_2')
    if sim_id_1 is None or sim_id_2 is None:
        return _error('Missing simulation IDs', 400)

    try:
        sim_id_1 = int(sim_id_1)
        sim_id_2 = int(sim_id_2)

        r1 = controller.visualisation_controller.results_controller.get_one_result(sim_id_1)
        r2 = controller.visualisation_controller.results_controller.get_one_result(sim_id_2)
        if r1 is None or r2 is None:
            return _error('One or both simulation IDs not found', 404)

        plots = PerformanceReport.generate_comparison_plots_base64(
            r1['report'],
            r2['report'],
            label1=f'Sim #{sim_id_1}',
            label2=f'Sim #{sim_id_2}',
        )
        return _success(200, plots=plots)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

@app.route('/api/report-plots', methods=['GET'])
def get_report_plots() -> ResponseReturnValue:
    """Generate and return base64-encoded plot images for the current simulation report."""
    if RD.reportData is None:
        return _error('No report available', 400)

    try:
        RD.reportData.generate_report()
        plots = RD.reportData.generate_plots_base64()
        return _success(200, plots=plots)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

@app.route('/api/report-plots/<int:sim_id>', methods=['GET'])
def get_saved_report_plots(sim_id: int) -> ResponseReturnValue:
    """Generate and return base64 plot images for a specific saved simulation report."""
    try:
        report = controller.visualisation_controller.results_controller.load_results(sim_id)
        if report is None:
            return _error('Simulation report not found', 404)

        report.generate_report()
        plots = report.generate_plots_base64()
        return _success(200, plots=plots)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

# -------------------------------
# Export API
# -------------------------------

@app.route('/api/export-current-report', methods=['GET'])
def export_current_report() -> ResponseReturnValue:
    """Export the current simulation report from the result screen."""
    try:
        if RD.reportData is None:
            return _error('No report available', 400)

        filepath = controller.visualisation_controller.results_controller.export_report(RD.reportData)
        if filepath and os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name='simulation_report.txt')

        return _error('Failed to generate report', 500)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

@app.route('/api/export-report/<int:sim_id>', methods=['GET'])
def export_report(sim_id: int) -> ResponseReturnValue:
    """Export a saved simulation report as a downloadable text file."""
    try:
        filepath = controller.visualisation_controller.exportSimulationReport(sim_id)
        if filepath and os.path.exists(filepath):
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f'simulation_{sim_id}_report.txt',
            )

        return _error('Failed to generate report', 500)
    except (TypeError, ValueError, KeyError) as e:
        return _error(str(e), 400)
    except (AttributeError, OSError) as e:
        return _error(str(e), 500)

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', os.environ.get('PORT', 8080)))
    app.run(host='127.0.0.1', port=port, debug=True)