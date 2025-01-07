import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.ignition_to_liftoff import flight_sim_ignition_to_liftoff
from rocketflightsim.liftoff_to_rail_clearance import flight_sim_liftoff_to_rail_clearance

from .test_configs import past_flights

class TestLiftoffToRailClearance(unittest.TestCase):
    def test_liftoff_to_rail_clearance(self):
        print("\nTesting liftoff to rail clearance function...")

        for past_flight in past_flights:
            print(f'For rocket: {past_flight.name}')

            t_liftoff = flight_sim_ignition_to_liftoff(past_flight.rocket, past_flight.launch_conditions)

            rail_clearance_state = flight_sim_liftoff_to_rail_clearance(past_flight.rocket, past_flight.launch_conditions, t_liftoff)[-1]
            height_at_rail_clearance = rail_clearance_state[1]
            height_of_rail = past_flight.launch_conditions.L_launch_rail * past_flight.launch_conditions.cos_rail_angle_to_vertical

            print(f"\tHeight at rail clearance: {height_at_rail_clearance} m")
            print(f"\tHeight of rail: {height_of_rail} m")

            print(f"\tSpeed at rail clearance: {np.sqrt(rail_clearance_state[2]**2 + rail_clearance_state[3]**2 + rail_clearance_state[4]**2)} m/s")

            assert height_at_rail_clearance < height_of_rail # the rocket is free of the rail's influence when the second lowest rail button/launch lug clears the rail, at which point the bottom of the rocket (which is what's stored as the rocket's z coordinate) is below the tip of the rail