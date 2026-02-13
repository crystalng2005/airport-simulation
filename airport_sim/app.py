import os
from flask import Flask, render_template, request, jsonify
from logic.simulation import SimulationController
from logic.presets import PresetController
from logic.visualisation import VisualisationController

# Explicitly configure templates and static directories
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)
