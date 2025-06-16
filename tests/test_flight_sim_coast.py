import sys
import os
from copy import deepcopy
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_sim_ignition_to_liftoff import sim_ignition_to_liftoff
from rocketflightsim.flight_sim_guided import sim_liftoff_to_rail_clearance
from rocketflightsim.flight_sim_unguided_boost import sim_unguided_boost
from rocketflightsim.flight_sim_coast import sim_coast_to_apogee
from rocketflightsim.tools.max_theoretical_conditions import max_theoretical_apogee

from .test_configs import past_flights

class TestSimCoastToApogee(unittest.TestCase):
    def test_sim_coast_to_apogee(self):
        print("\nTesting coast to apogee function...")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')

            t_liftoff = sim_ignition_to_liftoff(past_flight.rocket, past_flight.environment, past_flight.launchpad)

            rail_clearance_state = sim_liftoff_to_rail_clearance(past_flight.rocket, past_flight.environment, past_flight.launchpad, t_liftoff)[-1]

            burnout_state = sim_unguided_boost(past_flight.rocket, past_flight.environment, rail_clearance_state)[-1]

            apogee_state = sim_coast_to_apogee(past_flight.rocket, past_flight.environment, burnout_state)[-1]

            apogee_simulated = apogee_state[3]
            apogee_no_drag = max_theoretical_apogee(past_flight.rocket, past_flight.environment)
            difference = apogee_no_drag - apogee_simulated
            proportional_difference = difference / apogee_no_drag
            print(f"\tSimulated apogee: {round(apogee_simulated,2)} m\n\tNo-drag apogee: {round(apogee_no_drag,2)} m\n\tDifference: {round(difference,2)} m\n\tPercent difference: {round(proportional_difference*100,2)}%\n")

            assert difference >= 0 # Simulated apogee should be less than or equal to no-drag apogee