import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
# from rocketflightsim import constants as con
# from rocketflightsim import helper_functions as hfunc
from rocketflightsim.rocket_classes import Motor, Rocket, LaunchConditions
from rocketflightsim.flight_simulation import simulate_flight, simulate_airbrakes_flight


class TestFlightSimulation(unittest.TestCase):
    def test_flight_simulation(self):
            from test_configs import Juno3_rocket, Juno3_launch_conditions, default_airbrakes_model
    
            dataset, liftoff_index, launch_rail_cleared_index, burnout_index, apogee_index = simulate_flight(rocket=Juno3_rocket, launch_conditions=Juno3_launch_conditions, timestep=0.001)
            print(dataset[["time", "height", "speed"]].iloc[apogee_index - 1]*3.28084)
            ascent, time_of_max_deployment = simulate_airbrakes_flight(dataset.iloc[:burnout_index].copy(), rocket=Juno3_rocket, launch_conditions=Juno3_launch_conditions, airbrakes=default_airbrakes_model, timestep=0.001)
            print(ascent[["time", "height", "speed"]].iloc[-1]*3.28084)

            assert dataset["height"].iloc[apogee_index - 1] > 1000
            assert ascent["height"].iloc[-1] > 1000

if __name__ == '__main__':
    unittest.main()