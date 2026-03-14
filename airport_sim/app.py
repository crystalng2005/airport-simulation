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
    return jsonify({'success': False, 'error': 'No active simulation'}), 400


def _require_active_simulation() -> ResponseReturnValue | None:
    if not controller.visualisation_controller.hasSimulation():
        return _no_active_simulation_error()
    return None


def _read_json_body() -> dict[str, Any] | None:
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        return data
    return None


# -------------------------------
# Page routes
# -------------------------------

@app.route('/')
def index() -> str:
    return render_template('menu.html')


@app.route('/simulation-screen')
def simulation_page() -> str:
    return render_template('simulation_screen.html')


@app.route('/configure-simulation')
def configure_simulation_page() -> str:
    return render_template('configure_simulation.html')


@app.route('/results')
def results_page() -> str:
    return render_template('results.html')


@app.route('/result-screen')
def result_screen_page() -> str:
    return render_template('result_screen.html')


@app.route('/presets')
def presets_page() -> str:
    return render_template('presets.html')


# -------------------------------
# Simulation API
# -------------------------------

@app.route('/start', methods=['POST'])
def start_sim() -> ResponseReturnValue:
    data = _read_json_body()
    if data is None:
        return jsonify({'success': False, 'error': 'Invalid JSON body'}), 400

    try:
        controller.visualisation_controller.startSimulation(data)
        return jsonify({'success': True, 'message': 'Simulation started'}), 200
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/next-frame', methods=['POST'])
def next_frame() -> ResponseReturnValue:
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    controller.visualisation_controller.tick()
    return jsonify({'success': True, 'message': 'Frame advanced'}), 200


@app.route('/api/simulation-finished', methods=['GET'])
def is_simulation_finished() -> ResponseReturnValue:
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return jsonify({'success': False, 'error': 'No active simulation'}), 400

    return jsonify({
        'success': True,
        'finished': controller.visualisation_controller.isSimulationFinished(),
    }), 200


@app.route('/api/current-frame-actions', methods=['GET'])
def get_current_frame_actions() -> ResponseReturnValue:
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    actions = controller.visualisation_controller.getCurrentFrameActions()
    return jsonify({'success': True, 'actions': actions}), 200


@app.route('/api/current-time', methods=['GET'])
def get_current_time() -> ResponseReturnValue:
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    return jsonify({
        'success': True,
        'time': controller.visualisation_controller.getCurrentTime(),
    }), 200


@app.route('/api/aircraft/<plane_call_sign>', methods=['GET'])
def get_aircraft(plane_call_sign: str) -> ResponseReturnValue:
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    aircraft = controller.visualisation_controller.getAircraftByCallSign(plane_call_sign)
    if not aircraft:
        return jsonify({'success': False, 'error': 'Aircraft not found'}), 404

    return jsonify({'success': True, 'aircraft': aircraft.return_data()}), 200


@app.route('/api/number-of-runways', methods=['GET'])
def get_number_of_runways() -> ResponseReturnValue:
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    return jsonify({
        'success': True,
        'number': controller.visualisation_controller.getNumberOfRunways(),
    }), 200


@app.route('/api/runway-statuses', methods=['GET'])
def get_runway_status() -> ResponseReturnValue:
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    return jsonify({
        'success': True,
        'status': controller.visualisation_controller.getRunwayStatuses(),
    }), 200


@app.route('/api/runway-modes', methods=['GET'])
def get_runway_modes() -> ResponseReturnValue:
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return missing_simulation

    return jsonify({
        'success': True,
        'mode': controller.visualisation_controller.getRunwayModes(),
    }), 200


@app.route('/api/report', methods=['GET'])
def get_report() -> ResponseReturnValue:
    missing_simulation = _require_active_simulation()
    if missing_simulation is not None:
        return jsonify({'success': False, 'error': 'No active simulation'})

    report = controller.visualisation_controller.getCurrentSimulationReport()
    if report is None:
        return jsonify({'success': False, 'error': 'Report not ready'})

    return jsonify({'success': True, 'report': report})


# -------------------------------
# Preset API
# -------------------------------

@app.route('/api/get-preset-data/<int:preset_id>', methods=['GET'])
def get_preset_data(preset_id: int) -> ResponseReturnValue:
    try:
        preset_data = controller.visualisation_controller.getPresetData(preset_id)

        if preset_data:
            return jsonify({
                'success': True,
                'vars': preset_data.get('vars', {}),
                'planes': preset_data.get('planes', []),
                'report': preset_data.get('report', {}),
            })

        return jsonify({
            'success': False,
            'error': 'Preset not found',
        }), 404
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


@app.route('/api/get-presets', methods=['GET'])
def get_presets() -> ResponseReturnValue:
    try:
        presets = controller.visualisation_controller.getAvailablePresets()
        return jsonify({
            'success': True,
            'presets': presets,
        })
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


@app.route('/api/load-preset', methods=['POST'])
def load_preset() -> ResponseReturnValue:
    data = _read_json_body()
    if data is None:
        return jsonify({'success': False, 'error': 'Invalid JSON body'}), 400

    preset_id = data.get('preset_id')
    if preset_id is None:
        return jsonify({
            'success': False,
            'error': 'No preset_id provided',
        }), 400

    try:
        preset_data = controller.visualisation_controller.getPresetData(preset_id)
        if preset_data and 'vars' in preset_data:
            session['preset_mode'] = True
            session['preset_id'] = preset_id

            return jsonify({
                'success': True,
                'message': 'Preset loaded successfully',
            })

        return jsonify({
            'success': False,
            'error': 'Preset not found',
        }), 404
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


# -------------------------------
# Results and comparison API
# -------------------------------

@app.route('/api/get-all-results', methods=['GET'])
def get_all_results() -> ResponseReturnValue:
    try:
        results = controller.visualisation_controller.getAllSimulationResults()
        return jsonify({
            'success': True,
            'results': results,
        })
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


@app.route('/api/get-full-report/<int:sim_id>', methods=['GET'])
def get_full_report(sim_id: int) -> ResponseReturnValue:
    try:
        report = controller.visualisation_controller.getSimulationReport(sim_id)
        if report is None:
            return jsonify({
                'success': False,
                'error': 'Simulation report not found',
            }), 404

        return jsonify({
            'success': True,
            'report': report.get('report', {}),
        })
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


@app.route('/api/compare-simulations', methods=['POST'])
def compare_simulations() -> ResponseReturnValue:
    data = _read_json_body()
    if data is None:
        return jsonify({'success': False, 'error': 'Invalid JSON body'}), 400

    sim_id_1 = data.get('sim_id_1')
    sim_id_2 = data.get('sim_id_2')

    if sim_id_1 is None or sim_id_2 is None:
        return jsonify({'success': False, 'error': 'Missing simulation IDs'}), 400

    comparison = controller.visualisation_controller.compareSimulations(int(sim_id_1), int(sim_id_2))
    if comparison is None:
        return jsonify({'success': False, 'error': 'One or both simulation IDs not found'}), 404

    return jsonify({'success': True, 'comparison': comparison})


@app.route('/api/comparison-plots', methods=['POST'])
def comparison_plots() -> ResponseReturnValue:
    """Generate side-by-side bar chart plots comparing two simulation reports."""
    data = _read_json_body()
    if data is None:
        return jsonify({'success': False, 'error': 'Invalid JSON body'}), 400

    sim_id_1 = data.get('sim_id_1')
    sim_id_2 = data.get('sim_id_2')
    if sim_id_1 is None or sim_id_2 is None:
        return jsonify({'success': False, 'error': 'Missing simulation IDs'}), 400

    try:
        sim_id_1 = int(sim_id_1)
        sim_id_2 = int(sim_id_2)

        r1 = controller.visualisation_controller.results_controller.getOneResult(sim_id_1)
        r2 = controller.visualisation_controller.results_controller.getOneResult(sim_id_2)
        if r1 is None or r2 is None:
            return jsonify({'success': False, 'error': 'One or both simulation IDs not found'}), 404

        plots = PerformanceReport.generate_comparison_plots_base64(
            r1['report'],
            r2['report'],
            label1=f'Sim #{sim_id_1}',
            label2=f'Sim #{sim_id_2}',
        )
        return jsonify({'success': True, 'plots': plots})
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/report-plots', methods=['GET'])
def get_report_plots() -> ResponseReturnValue:
    """Generate and return base64-encoded plot images for the current simulation report."""
    if RD.reportData is None:
        return jsonify({'success': False, 'error': 'No report available'}), 400

    try:
        RD.reportData.generateReport()
        plots = RD.reportData.generate_plots_base64()
        return jsonify({'success': True, 'plots': plots})
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/report-plots/<int:sim_id>', methods=['GET'])
def get_saved_report_plots(sim_id: int) -> ResponseReturnValue:
    """Generate and return base64 plot images for a specific saved simulation report."""
    try:
        report = controller.visualisation_controller.results_controller.load_results(sim_id)
        if report is None:
            return jsonify({'success': False, 'error': 'Simulation report not found'}), 404

        report.generateReport()
        plots = report.generate_plots_base64()
        return jsonify({'success': True, 'plots': plots})
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# -------------------------------
# Export API
# -------------------------------

@app.route('/api/export-current-report', methods=['GET'])
def export_current_report() -> ResponseReturnValue:
    """Export the current simulation report from the result screen."""
    try:
        if RD.reportData is None:
            return jsonify({'success': False, 'error': 'No report available'}), 400

        filepath = controller.visualisation_controller.results_controller.export_report(RD.reportData)
        if filepath and os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name='simulation_report.txt')

        return jsonify({'success': False, 'error': 'Failed to generate report'}), 500
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export-report/<int:sim_id>', methods=['GET'])
def export_report(sim_id: int) -> ResponseReturnValue:
    try:
        filepath = controller.visualisation_controller.exportSimulationReport(sim_id)
        if filepath and os.path.exists(filepath):
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f'simulation_{sim_id}_report.txt',
            )

        return jsonify({
            'success': False,
            'error': 'Failed to generate report',
        }), 500
    except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', os.environ.get('PORT', 8080)))
    app.run(host='127.0.0.1', port=port, debug=True)
