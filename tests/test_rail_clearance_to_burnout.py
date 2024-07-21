import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.ignition_to_liftoff import flight_sim_ignition_to_liftoff
from rocketflightsim.liftoff_to_rail_clearance import flight_sim_liftoff_to_rail_clearance
from rocketflightsim.rail_clearance_to_burnout import flight_sim_rail_clearance_to_burnout

from rocketflightsim.tools.max_theoretical_conditions import max_theoretical_speed, max_theoretical_accel_motor

from .test_configs import past_flights

class TestRailClearanceToBurnout(unittest.TestCase):
    def test_rail_clearance_to_burnout(self):
        print("\nTesting rail clearance to burnout function...")

        for past_flight in past_flights:
            print(f'For rocket: {past_flight.name}')

            # first, simulate flight with the function
            t_liftoff = flight_sim_ignition_to_liftoff(past_flight.rocket, past_flight.launch_conditions)

            flight_to_rail_clearance = flight_sim_liftoff_to_rail_clearance(past_flight.rocket, past_flight.launch_conditions, t_liftoff)

            rail_clearance_state = flight_to_rail_clearance[-1]

            flight_to_burnout = flight_sim_rail_clearance_to_burnout(past_flight.rocket, past_flight.launch_conditions, rail_clearance_state)

            # next, compare to the maximum theoretical airspeed and acceleration
            max_airspeed_theoretical = max_theoretical_speed(past_flight.rocket, past_flight.launch_conditions)
            max_acceleration_theoretical = max_theoretical_accel_motor(past_flight.rocket, past_flight.launch_conditions)

            max_airspeed_simulated = 0
            max_acceleration_simulated = 0
            for state_vector in flight_to_burnout:
                airspeed = np.sqrt(state_vector[2]**2 + state_vector[3]**2 + state_vector[4]**2)
                acceleration = np.sqrt(state_vector[5]**2 + state_vector[6]**2 + state_vector[7]**2)
                if airspeed > max_airspeed_simulated:
                    max_airspeed_simulated = airspeed
                if acceleration > max_acceleration_simulated:
                    max_acceleration_simulated = acceleration
                # TODO: it's possible for a rocket to have its max speed/accel on the launch rail (even though it's very rare to pick a launch rail that you won't clear before you stop accelerating). If max speed is in the first instant after clearance, have it go back and check for faster speeds/higher accels in the flight_to_rail_clearance list

            difference = max_airspeed_theoretical - max_airspeed_simulated
            proportional_difference = difference / max_airspeed_simulated

            print(f"\tSimulated max airspeed: {round(max_airspeed_simulated, 2)} m/s\n\tMax theoretical airspeed: {round(max_airspeed_theoretical, 2)} m/s\n\tDifference: {round(difference, 2)} m/s\n\tPercent difference: {round(proportional_difference*100, 2)}%\n")
            assert difference > 0

            difference = max_acceleration_theoretical - max_acceleration_simulated
            proportional_difference = difference / max_acceleration_theoretical
            print(f"\tSimulated max acceleration: {round(max_acceleration_simulated, 2)} m/s\n\tMax theoretical acceleration: {round(max_acceleration_theoretical, 2)} m/s\n\tDifference: {round(difference, 2)} m/s\n\tPercent difference: {round(proportional_difference*100, 2)}%\n")
            assert difference > 0

            # next, compare max simulated speed and acceleration to flight data
            # TODO

            # then, check if total impulse were added to the rocket's dry mass in the first instant after ignition, it would give a higher max acceleration than the simulator predicts
            # TODO