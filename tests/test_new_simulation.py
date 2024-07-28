import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_simulation import flight_sim_ignition_to_apogee

from .test_configs import past_flights
from .test_configs import Juno3_rocket, Juno3_launch_conditions

class TestNewSimulation(unittest.TestCase):
    def test_new_simulation(self):
        print("Testing new simulation")

        for past_flight in past_flights:
            print(f'For rocket: {past_flight.name}')

            new_combined_functions_apogee_state = flight_sim_ignition_to_apogee(past_flight.rocket, past_flight.launch_conditions, 0.001)
            apogee_simulated = new_combined_functions_apogee_state[1]

            apogee_actual = past_flight.apogee
            difference = apogee_simulated - apogee_actual
            proportional_difference = difference / apogee_actual
            print(f"\tSimulated apogee: {round(apogee_simulated,2)} m\n\tActual apogee: {round(apogee_actual,2)} m\n\tDifference: {round(difference,2)} m\n\tPercent difference: {round(proportional_difference*100,2)}%\n")

            assert np.abs(proportional_difference) < 0.1


        # # test speed new vs old function (a little biased towards the new way because the old one still packs things into dfs. However, that shouldn't account for all of the ~18% speed improvement)

        # import time

        # time_start = time.time()
        # for i in range(100):
        #     dataset, _, _, _, _ = simulate_flight(rocket=Juno3_rocket, launch_conditions=Juno3_launch_conditions, timestep=0.001)
        #     print(i)
        # print(time.time() - time_start)

        # time_start = time.time()
        # for i in range(100):
        #     new_combined_functions_apogee_state = flight_sim_ignition_to_apogee(Juno3_rocket, Juno3_launch_conditions, 0.001)
        #     print(i)
        # print(time.time() - time_start)