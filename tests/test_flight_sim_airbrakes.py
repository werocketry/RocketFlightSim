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
from rocketflightsim.flight_sim_airbrakes import sim_max_airbrakes_deployment_to_apogee

from .test_configs import past_flights, example_airbrakes_model

class TestAirbrakesToApogee(unittest.TestCase):
    def test_airbrakes_to_apogee(self):
        print("\nTesting airbrakes to apogee function...")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')

            t_liftoff = sim_ignition_to_liftoff(past_flight.rocket, past_flight.environment, past_flight.launchpad)

            rail_clearance_state = sim_liftoff_to_rail_clearance(past_flight.rocket, past_flight.environment, past_flight.launchpad, t_liftoff)[-1]

            burnout_state = sim_unguided_boost(past_flight.rocket, past_flight.environment, rail_clearance_state)[-1]

            apogee_state_no_airbrakes = sim_coast_to_apogee(past_flight.rocket, past_flight.environment, burnout_state)[-1]

            apogee_state = sim_max_airbrakes_deployment_to_apogee(past_flight.rocket, past_flight.environment, example_airbrakes_model, burnout_state)[-1]

            apogee_simulated_no_airbrakes = apogee_state_no_airbrakes[3]
            apogee_simulated = apogee_state[3]

            difference = apogee_simulated_no_airbrakes - apogee_simulated
            proportional_difference = difference / apogee_simulated_no_airbrakes
            print(f"\tSimulated apogee no airbrake deployment: {round(apogee_simulated_no_airbrakes,2)} m\n\tSimulated apogee max airbrake deployment: {round(apogee_simulated,2)} m\n\tDifference: {round(difference,2)} m\n\tPercent difference: {round(proportional_difference*100,2)}%\n")

            assert difference > 0 # actuating the airbrakes should decrease apogee

# TODO: add test for sim function with deployment as a function of height?