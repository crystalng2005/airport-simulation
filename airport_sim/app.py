# Flask Entry Point (MainController logic)
import os
from flask import Flask, render_template, request, jsonify, session
from logic.presets import PresetController
from logic.visualisation import VisualisationController
from logic.report import PerformanceReport
from datetime import datetime
import logic.globals.reportData as RD
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

class MainController:
    def __init__(self):
        self.is_available = True
        self.preset_controller = PresetController()
        self.visualisation_controller = VisualisationController()

    def validateParameters(self, runways, inbound_flow, outbound_flow):
        pass # Consider if it is necessary to validate parameters or will frontend handle this part? (by fixing the potential input)

controller = MainController()

@app.route('/')
def index():
    # Renders the home page (Main Menu)
    return render_template('menu.html')

@app.route('/start', methods=['POST'])
def start_sim():
    try:
        data = request.get_json()
        controller.visualisation_controller.startSimulation(data)

        controller.is_available = False

        return jsonify({'success': True, 'message': 'Simulation started'}), 200

    except Exception as e:
        return jsonify({'success': False, 'errors': [str(e)]}), 500


@app.route('/tick', methods=['POST'])
def tick():
    if controller.is_available or not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'errors': ['No active simulation']}), 400

    controller.visualisation_controller.tick()
    return jsonify({'success': True, 'message': 'Tick processed'}), 200
    
# @app.route('/visualisation/data', methods=['GET'])
# def getVisualisationData():
    
#     aircraft_data = controller.visualisation_controller.getAircraftData(controller.simulation)
#     return jsonify({'success': True, 'data': aircraft_data}), 200

#Simulation screen Routes
@app.route('/simulation-screen')
def simulation_page():
    """Display simulation screen page"""
    return render_template('simulation_screen.html')

@app.route('/configure-simulation')
def configure_simulation_page():
    return render_template('configure_simulation.html')

@app.route('/api/runway-count', methods=['GET'])
def get_runway_count():
    """Get total number of runways in current simulation"""
    if not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'error': 'No active simulation'}), 400

    return jsonify({
        'success': True,
        'count': controller.visualisation_controller.getNumberOfRunways()
    }), 200


@app.route('/api/simulation-finished', methods=['GET'])
def is_simulation_finished():
    """Check if simulation has finished"""
    if not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'error': 'No active simulation'}), 400

    return jsonify({
        'success': True,
        'finished': controller.visualisation_controller.isSimulationFinished()
    }), 200


@app.route('/api/get-preset-data/<int:preset_id>', methods=['GET'])
def get_preset_data(preset_id):
    """Get full preset data for configuration form"""
    try:
        preset_data = controller.visualisation_controller.getPresetData(preset_id)
        
        if preset_data:
            return jsonify({
                "success": True,
                "vars": preset_data.get("vars", {}),
                "planes": preset_data.get("planes", []),
                "report": preset_data.get("report", {})
            })
        else:
            return jsonify({
                "success": False,
                "error": "Preset not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
#Presets Routes

@app.route('/presets')
def presets_page():
    """Display presets selection page"""
    return render_template('presets.html')


@app.route('/api/get-presets', methods=['GET'])
def get_presets():
    """Get available presets for the presets page"""
    try:
        print('🔍 /api/get-presets called')
        
        presets = controller.visualisation_controller.getAvailablePresets()
        
        
        return jsonify({
            "success": True,
            "presets": presets
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/load-preset', methods=['POST'])
def load_preset():
    
    try:
        data = request.get_json()
        preset_id = data.get('preset_id')
        
        if preset_id is None:
            return jsonify({
                "success": False,
                "error": "No preset_id provided"
            }), 400
        
   
        preset_data = controller.visualisation_controller.getPresetData(preset_id)
        
        if preset_data and "vars" in preset_data:
            # Store in session
            session['preset_mode'] = True
            session['preset_id'] = preset_id
            
            return jsonify({
                "success": True,
                "message": "Preset loaded successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": preset_data.get("error")
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



# Results & Comparison Routes

@app.route('/results')
def results_page():
    """Display results page"""
    return render_template('results.html')

@app.route('/result-screen')
def result_screen_page():
    return render_template('result_screen.html')


@app.route('/api/get-all-results', methods=['GET'])
def get_all_results():
    
    try:
        results = controller.visualisation_controller.getAllSimulationResults()
        
        return jsonify({
            "success": True,
            "results": results
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/get-full-report/<int:sim_id>', methods=['GET'])
def get_full_report(sim_id):
   
    try:
        report = controller.visualisation_controller.getSimulationReport(sim_id)
        return jsonify(report)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/compare-simulations', methods=['POST']) # Is this used anywhere?
def compare_simulations(self, sim_id_1, sim_id_2):
    comparison = controller.visualisation_controller.compareSimulations(int(sim_id_1), int(sim_id_2))
    if comparison is None:
        return jsonify({"success": False, "error": "One or both simulation IDs not found"}), 404
    return jsonify({"success": True, "comparison": comparison})


@app.route('/api/export-report/<int:sim_id>', methods=['GET'])
def export_report(sim_id):  
    
    try:
        from flask import send_file
        
        filepath = controller.visualisation_controller.exportSimulationReport(sim_id)
        
        if filepath and os.path.exists(filepath):
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f"simulation_{sim_id}_report.txt"
            )
        else:
            return jsonify({
                "success": False,
                "error": "Failed to generate report"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route('/api/current-frame-actions', methods=['GET'])
def get_current_frame_actions():
    if not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'errors': ['No active simulation']}), 400
    
    actions = controller.visualisation_controller.getCurrentFrameActions()
    return jsonify({'success': True, 'actions': actions}), 200

@app.route('/api/current-time', methods=['GET'])
def get_current_time():
    if not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'errors': ['No active simulation']}), 400

    return jsonify({
        'success': True,
        'time': controller.visualisation_controller.getCurrentTime()
    }), 200

@app.route('/api/next-frame', methods=['POST'])
def next_frame():
    if not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'errors': ['No active simulation']}), 400

    controller.visualisation_controller.tick()
    return jsonify({'success': True, 'message': 'Frame advanced'}), 200

@app.route('/api/aircraft/<plane_call_sign>', methods=['GET'])
def get_aircraft(plane_call_sign):
    if not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'errors': ['No active simulation']}), 400
    
    aircraft = controller.visualisation_controller.getAircraftByCallSign(plane_call_sign)
    if not aircraft:
        return jsonify({'success': False, 'errors': ['Aircraft not found']}), 404
    
    return jsonify({'success': True, 'aircraft': aircraft.return_data()}), 200

@app.route('/api/number-of-runways', methods=['GET'])
def get_number_of_runways():
    if not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'errors': ['No active simulation']}), 400

    return jsonify({
        'success': True,
        'number': controller.visualisation_controller.getNumberOfRunways()
    }), 200

@app.route('/api/runway-statuses', methods=['GET'])
def get_runway_status():
    if not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'errors': ['No active simulation']}), 400

    return jsonify({
        'success': True,
        'status': controller.visualisation_controller.getRunwayStatuses()
    }), 200

@app.route('/api/runway-modes', methods=['GET'])
def get_runway_modes():
    if not controller.visualisation_controller.hasSimulation():
        return jsonify({'success': False, 'errors': ['No active simulation']}), 400

    return jsonify({
        'success': True,
        'mode': controller.visualisation_controller.getRunwayModes()
    }), 200

@app.route('/api/report', methods=['GET'])
def get_report():
    if controller.visualisation_controller.hasSimulation():
        report = controller.visualisation_controller.getCurrentSimulationReport()
        if report is None:
            return jsonify({'success': False, 'error': 'Report not ready'})
        return jsonify({'success': True, 'report': report})
    return jsonify({'success': False, 'error': 'No active simulation'})


    
   
if __name__ == '__main__':
    app.run(debug=True)