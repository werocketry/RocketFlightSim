import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_simulation import simulate_flight, simulate_airbrakes_flight_max_deployment

from .test_configs import past_flights
from .test_configs import Juno3_rocket, Juno3_launch_conditions

from example_configurations import default_airbrakes_model

class TestFlightSimulationEmpirical(unittest.TestCase):
    def test_flight_simulation_empirical(self):
            print("Testing flight simulation")

            for flight in past_flights:
                dataset, liftoff_index, launch_rail_cleared_index, burnout_index, apogee_index = simulate_flight(rocket=flight.rocket, launch_conditions=flight.launch_conditions, timestep=0.001)

                apogee_simulated = dataset["height"].iloc[apogee_index - 1]
                apogee_actual = flight.apogee
                difference = apogee_simulated - apogee_actual
                proportional_difference = difference / apogee_actual
                print(f"Flight {flight.name}: \n\tSimulated apogee: {round(apogee_simulated,2)} m\n\tActual apogee: {round(apogee_actual,2)} m\n\tDifference: {round(difference,2)} m\n\tPercent difference: {round(proportional_difference*100,2)}%\n")

                assert np.abs(proportional_difference) < 0.1
            print("\n--------------------")


class TestAirbrakesFlightSimulationMaxDeployment(unittest.TestCase):
     def test_airbrakes_flight_max_deployment_simulation(self):
            print("\n--------------------")
            print("Testing airbrakes flight simulation")
            
            dataset, liftoff_index, launch_rail_cleared_index, burnout_index, apogee_index = simulate_flight(rocket=Juno3_rocket, launch_conditions=Juno3_launch_conditions, timestep=0.001)
            print(f"Burnout: \n\tHeight: {dataset['height'].iloc[burnout_index - 1]} m\n\tAirspeed: {dataset['airspeed'].iloc[burnout_index - 1]} m/s\n\tTime: {dataset['time'].iloc[burnout_index - 1]} s\n")
            print(f"No-airbraking apogee: \n\tHeight: {dataset['height'].iloc[apogee_index - 1]} m\n\tTime: {dataset['time'].iloc[apogee_index - 1]} s\n")
            # TODO: make it take the actual flight data at burnout and sim from there
            
            ascent = simulate_airbrakes_flight_max_deployment(dataset.iloc[:burnout_index].copy(), rocket=Juno3_rocket, launch_conditions=Juno3_launch_conditions, airbrakes=default_airbrakes_model, timestep=0.001)
            print(f"Max deployment airbrakes apogee: \n\tHeight: {ascent['height'].iloc[-1]} m\n\tTime: {ascent['time'].iloc[-1]} s\n\n")
            print("--------------------")

            assert ascent["height"].iloc[-1] > 1000
            assert ascent["height"].iloc[-1] < dataset["height"].iloc[apogee_index - 1]
            assert ascent["time"].iloc[-1] < dataset["time"].iloc[apogee_index - 1]
            # assert ascent["airspeed"].iloc[-1] < dataset["airspeed"].iloc[apogee_index - 1] ?


if __name__ == '__main__':
    unittest.main()