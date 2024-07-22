import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.ignition_to_liftoff import flight_sim_ignition_to_liftoff
from rocketflightsim.liftoff_to_rail_clearance import flight_sim_liftoff_to_rail_clearance
from rocketflightsim.rail_clearance_to_burnout import flight_sim_rail_clearance_to_burnout
from rocketflightsim.burnout_to_apogee import flight_sim_burnout_to_apogee
from rocketflightsim.airbrakes_to_apogee import flight_sim_max_airbrakes_deployment_to_apogee

from .test_configs import past_flights, default_airbrakes_model

class TestAirbrakesToApogee(unittest.TestCase):
    def test_airbrakes_to_apogee(self):
        print("\nTesting airbrakes to apogee function...")

        for past_flight in past_flights:
            print(f'For rocket: {past_flight.name}')

            t_liftoff = flight_sim_ignition_to_liftoff(past_flight.rocket, past_flight.launch_conditions)

            rail_clearance_state = flight_sim_liftoff_to_rail_clearance(past_flight.rocket, past_flight.launch_conditions, t_liftoff)[-1]

            burnout_state = flight_sim_rail_clearance_to_burnout(past_flight.rocket, past_flight.launch_conditions, rail_clearance_state)[-1]

            apogee_state_no_airbrakes = flight_sim_burnout_to_apogee(past_flight.rocket, past_flight.launch_conditions, burnout_state)[-1]

            apogee_state = flight_sim_max_airbrakes_deployment_to_apogee(past_flight.rocket, past_flight.launch_conditions, default_airbrakes_model, burnout_state)[-1]

            apogee_simulated_no_airbrakes = apogee_state_no_airbrakes[1]
            apogee_simulated = apogee_state[1]

            difference = apogee_simulated_no_airbrakes - apogee_simulated
            proportional_difference = difference / apogee_simulated_no_airbrakes
            print(f"\tSimulated apogee no airbrake deployment: {round(apogee_simulated_no_airbrakes,2)} m\n\tSimulated apogee max airbrake deployment: {round(apogee_simulated,2)} m\n\tDifference: {round(difference,2)} m\n\tPercent difference: {round(proportional_difference*100,2)}%\n")

            assert difference > 0

# TODO: add test for sim function with deployment as a function of height?