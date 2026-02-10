# Flask Entry Point (MainController logic)from flask import Flask, render_template, request

from logic.simulation import SimulationController

app = Flask(__name__)

@app.route('/')
def index():
    pass

@app.route('/start', methods=['POST'])
def start_sim():
    pass

if __name__ == '__main__':
    app.run(debug=True)