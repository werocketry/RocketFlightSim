import sys
import os
from copy import deepcopy
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_stages_combined import flight_sim_ignition_to_apogee
from rocketflightsim.flight_sim_parachute import sim_parachute

from .test_configs import past_flights

# currently just test that the function works, without comparing the output to much
# TODO test for the function using theoretical terminal velocity
# TODO add an example with both a drogue and main
class TestSimParachute(unittest.TestCase):
    def test_sim_parachute(self):
        print("\nTesting parachute flight simulation...\n")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')

            apogee_state = flight_sim_ignition_to_apogee(past_flight.rocket, past_flight.environment, past_flight.launchpad)[-1]
            print(f"Location at apogee: {apogee_state[1].round(2)} m east, {apogee_state[2].round(2)} m north, {apogee_state[3].round(2)} m above ground level")

            touchdown_state = sim_parachute(past_flight.rocket, past_flight.environment, (*apogee_state[:7],), past_flight.parachute)[-1]

            print(f"Location at touchdown: {touchdown_state[1].round(2)} m east, {touchdown_state[2].round(2)} m north, {touchdown_state[3].round(2)} m above ground level")

            assert touchdown_state[3] <= 0 # check that the rocket has landed
            print()