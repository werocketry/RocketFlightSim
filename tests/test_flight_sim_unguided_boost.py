import sys
import os
from copy import deepcopy
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_sim_ignition_to_liftoff import sim_ignition_to_liftoff
from rocketflightsim.flight_sim_guided import sim_liftoff_to_rail_clearance
from rocketflightsim.flight_sim_unguided_boost import sim_unguided_boost

from rocketflightsim.tools.max_theoretical_conditions import max_theoretical_speed, max_theoretical_accel_motor

from .test_configs import past_flights

class TestSimUnguidedBoost(unittest.TestCase):
    def test_sim_unguided_boost(self):
        print("\nTesting unguided boost function...")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')

            # first, simulate flight with the function
            t_liftoff = sim_ignition_to_liftoff(past_flight.rocket, past_flight.environment, past_flight.launchpad)

            flight_to_rail_clearance = sim_liftoff_to_rail_clearance(past_flight.rocket, past_flight.environment, past_flight.launchpad, t_liftoff)

            rail_clearance_state = flight_to_rail_clearance[-1]

            flight_to_burnout = sim_unguided_boost(past_flight.rocket, past_flight.environment, rail_clearance_state)

            # next, compare to the maximum theoretical airspeed and acceleration
            max_airspeed_theoretical = max_theoretical_speed(past_flight.rocket, past_flight.environment)
            max_acceleration_theoretical = max_theoretical_accel_motor(past_flight.rocket, past_flight.environment)

            max_airspeed_simulated = 0
            max_acceleration_simulated = 0
            for state_vector in flight_to_burnout:
                airspeed = np.sqrt(state_vector[4]**2 + state_vector[5]**2 + state_vector[6]**2)
                acceleration = np.sqrt(state_vector[7]**2 + state_vector[8]**2 + state_vector[9]**2)
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

            # TODO check that if total impulse were added to the rocket's dry mass in the first instant after ignition, it would give a higher max acceleration than the simulator predicts