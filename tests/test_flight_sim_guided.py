import sys
import os
from copy import deepcopy
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_sim_ignition_to_liftoff import sim_ignition_to_liftoff
from rocketflightsim.flight_sim_guided import sim_liftoff_to_rail_clearance

from .test_configs import past_flights

class TestSimLiftoffToRailClearance(unittest.TestCase):
    def test_sim_liftoff_to_rail_clearance(self):
        print("\nTesting liftoff to rail clearance function...")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')

            t_liftoff = sim_ignition_to_liftoff(past_flight.rocket, past_flight.environment, past_flight.launchpad)

            rail_clearance_state = sim_liftoff_to_rail_clearance(past_flight.rocket, past_flight.environment, past_flight.launchpad, t_liftoff)[-1]
            height_at_rail_clearance = rail_clearance_state[3]
            height_of_rail = past_flight.launchpad.rail_length * past_flight.launchpad.rail_unit_vector_z

            print(f"\tHeight at rail clearance: {height_at_rail_clearance} m")
            print(f"\tHeight of rail: {height_of_rail} m")

            print(f"\tSpeed at rail clearance: {np.sqrt(rail_clearance_state[4]**2 + rail_clearance_state[5]**2 + rail_clearance_state[6]**2)} m/s")
            print(f"\tTime at rail clearance: {rail_clearance_state[0]} s")

            assert height_at_rail_clearance < height_of_rail # the rocket is free of the rail's influence when the second lowest rail button/launch lug clears the rail, at which point the bottom of the rocket (which is what's stored as the rocket's z coordinate) is below the tip of the rail