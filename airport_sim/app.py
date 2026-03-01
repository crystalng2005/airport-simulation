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

if __name__ == '__main__':
    app.run(debug=True)