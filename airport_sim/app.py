# Flask Entry Point (MainController logic)
import os
from flask import Flask, render_template, request, jsonify
from logic.simulation import SimulationController
from logic.presets import PresetController
from logic.visualisation import VisualisationController

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

class MainController:
    def __init__(self):
        self.simulation = None
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

        runways = data.get('runways')
        inbound_flow = data.get('inbound_flow')
        outbound_flow = data.get('outbound_flow')
        departure_runways = data.get('departure_runways')
        landing_runways = data.get('landing_runways')
        mixed_runways = data.get('mixed_runways')
        cancellation_time = data.get('cancellation_time')

        controller.simulation = SimulationController(
            departures_per_hour=int(outbound_flow),
            landings_per_hour=int(inbound_flow),
            total_runways=int(runways),
            departure_runways=int(departure_runways),
            landing_runways=int(landing_runways),
            mixed_runways=int(mixed_runways),
            cancellation_time=int(cancellation_time)
        )

        controller.is_available = False # Simulation is ongoing

        return jsonify({'success': True, 'message': 'Simulation started'}), 200

    except Exception as e:
        return jsonify({'success': False, 'errors': [str(e)]}), 500


@app.route('/tick', methods=['POST'])
def tick():
    if not controller.is_available or controller.simulation is None:
        return jsonify({'success': False, 'errors': ['No active simulation']}), 400
    
    controller.simulation.update()
    return jsonify({'success': True, 'message': 'Tick processed'}), 200
    
@app.route('/visualisation/data', methods=['GET'])
def getVisualisationData():
    
    aircraft_data = controller.visualisation_controller.getAircraftData(controller.simulation)
    return jsonify({'success': True, 'data': aircraft_data}), 200

#Presets Routes

@app.route('/presets')
def presets_page():
    """Display presets selection page"""
    return render_template('presets.html')


@app.route('/api/get-presets', methods=['GET'])
def get_presets():
    
    try:
        
        presets = vis_controller.getAvailablePresets()
        
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
        
   
        preset_data = vis_controller.loadPresetData(preset_id)
        
        if preset_data["success"]:
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


@app.route('/api/get-all-results', methods=['GET'])
def get_all_results():
    
    try:
        results = vis_controller.getAllSimulationResults()
        
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
        report = vis_controller.getSimulationReport(sim_id)
        return jsonify(report)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/compare-simulations', methods=['POST'])
def compare_simulations():
   
    try:
        data = request.get_json()
        sim_id_1 = data.get('sim_id_1')
        sim_id_2 = data.get('sim_id_2')
        
        if sim_id_1 is None or sim_id_2 is None:
            return jsonify({
                "success": False,
                "error": "Both simulation IDs required"
            }), 400
        
        comparison = vis_controller.compareSimulations(int(sim_id_1), int(sim_id_2))
        return jsonify(comparison)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/export-report/<int:sim_id>', methods=['GET'])
def export_report(sim_id):
    
    try:
        from flask import send_file
        
        filepath = vis_controller.exportSimulationReport(sim_id, format="txt")
        
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

    
   
if __name__ == '__main__':
    app.run(debug=True)