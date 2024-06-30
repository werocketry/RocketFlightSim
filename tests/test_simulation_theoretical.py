import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_simulation import simulate_flight
from rocketflightsim.tools.max_theoretical_conditions import max_theoretical_accel_motor, max_theoretical_speed

from .test_configs import past_flights

class TestFlightSimulationTheoreticalMaxs(unittest.TestCase):
    def test_flight_simulation_theoretical_max(self):
            print("Testing flight simulation")

            for flight in past_flights:
                dataset, liftoff_index, launch_rail_cleared_index, burnout_index, apogee_index = simulate_flight(rocket=flight.rocket, launch_conditions=flight.launch_conditions, timestep=0.001)

                max_airspeed_theoretical = max_theoretical_speed(flight.rocket, flight.launch_conditions)
                max_airspeed_simulated = dataset['airspeed'].max()
                difference = max_airspeed_theoretical - max_airspeed_simulated
                proportional_difference = difference / max_airspeed_simulated

                print(f"Flight {flight.name}: \n\tSimulated max airspeed: {round(max_airspeed_simulated,2)} m\n\tMax theoretical airspeed: {round(max_airspeed_theoretical,2)} m\n\tDifference: {round(difference,2)} m\n\tPercent difference: {round(proportional_difference*100,2)}%\n")
                assert difference > 0

                max_acceleration_theoretical = max_theoretical_accel_motor(rocket = flight.rocket, launch_conditions = flight.launch_conditions)
                # TODO: max_acceleration_simulated = 
                

                # maybe add apogee if max theoretical added to the tool
                apogee_simulated = dataset["z"].iloc[apogee_index - 1]
                
            print("\n--------------------")