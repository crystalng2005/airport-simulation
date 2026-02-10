# Flask Entry Point (MainController logic)from flask import Flask, render_template, request
from flask import Flask, render_template, request
from logic.simulation import SimulationController

app = Flask(__name__)

class MainController:
    def __init__(self):
        self.simulation = None
        self.is_available = True

controller = MainController()

@app.route('/')
def index():
    pass

@app.route('/start', methods=['POST'])
def start_sim():
    pass

if __name__ == '__main__':
    app.run(debug=True)