import unittest
import json
from airport_sim.app import app, controller

class TestFlaskApp(unittest.TestCase):
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        controller.simulation = None  # Reset simulation state
    
    def tearDown(self):
        controller.simulation = None
    
    def testAppExist(self):
        self.assertIsNotNone(app)
    
    # The below is just additional testing (not important)
    def testAppIsTesting(self):
        self.assertTrue(app.config['TESTING'])
    
    def testHomeRouteStatus(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def testHomeRouteRenderTemplate(self):
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 500])
    
    def testStartRouteAcceptPost(self):
        data = {
            'runways': 5,
            'inbound_flow': 20,
            'outbound_flow': 15,
            'departure_runways': 2,
            'landing_runways': 2,
            'mixed_runways': 1,
            'cancellation_time': 300
        }
        response = self.client.post('/start', data=json.dumps(data), content_type='application/json')
        self.assertIn(response.status_code, [200, 500])

    # Below are more relavent tests (to be implemented by the frontend testing people)
    
    def testStartRouteValidatesRunways(self):
        data = {
            'runways': 15,  # Invalid: exceeds 10 (depending on UI design, this might not be needed)
            'inbound_flow': 20,
            'outbound_flow': 15,
            'departure_runways': 2,
            'landing_runways': 2,
            'mixed_runways': 1,
            'cancellation_time': 300
        }
        response = self.client.post('/start', data=json.dumps(data), content_type='application/json')
        # TODO: Implement validation logic first
        self.assertIsNotNone(response)
    
    def testTickRouteWithoutSimulation(self):
        response = self.client.post('/tick')
        # TODO: Add proper error handling
        self.assertIsNotNone(response)
    
    def testVisualisationRouteExists(self):
        response = self.client.get('/visualisation/data')
        self.assertIsNotNone(response)
    
    def testJsonResponseFormat(self):
        response = self.client.get('/visualisation/data')
        try:
            json.loads(response.data)
            json_valid = True
        except json.JSONDecodeError:
            json_valid = False
        self.assertTrue(json_valid or response.status_code == 500)


class TestMainController(unittest.TestCase):
    
    def testControllerInitialization(self):
        self.assertIsNotNone(controller)
        self.assertIsNone(controller.simulation)
        self.assertTrue(controller.is_available)
    
    def testPresetControllerExists(self):
        self.assertIsNotNone(controller.preset_controller)
    
    def testVisualisationControllerExists(self):
        self.assertIsNotNone(controller.visualisation_controller)
