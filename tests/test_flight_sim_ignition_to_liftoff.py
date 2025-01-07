import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.ignition_to_liftoff import flight_sim_ignition_to_liftoff

from .test_configs import past_flights

# currently just test that the function works, without comparing the output to much
class TestIgnitionToLiftoff(unittest.TestCase):
    def test_ignition_to_liftoff(self):
        print("\nTesting ignition to liftoff function...")

        for past_flight in past_flights:
            print(f'For rocket: {past_flight.name}')

            t_liftoff = flight_sim_ignition_to_liftoff(past_flight.rocket, past_flight.launch_conditions)

            print(f"\tTime of liftoff: {t_liftoff} s")
            
            assert t_liftoff >= 0 # the 'or equal to' lets thrust curves that don't start at 0 pass, even though they shouldn't start at 0 if they're made properly