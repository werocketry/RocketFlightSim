import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_simulation import simulate_flight

from .test_configs import past_flights

class TestNewSimulation(unittest.TestCase):
    def test_new_simulation(self):
        print("Testing new simulation")
        from rocketflightsim.flight_simulation import flight_sim_ignition_to_apogee

        for past_flight in past_flights:
            print(f'For rocket: {past_flight.name}')

            new_combined_functions_apogee_state = flight_sim_ignition_to_apogee(past_flight.rocket, past_flight.launch_conditions, 0.001)

            print(f"With new combined functions, the state at apogee is:\n {new_combined_functions_apogee_state}")
            print('\n')