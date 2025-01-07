import sys
import os
from copy import deepcopy
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_sim_ignition_to_liftoff import sim_ignition_to_liftoff

from .test_configs import past_flights

# currently just test that the function works, without comparing the output to much
class TestSimIgnitionToLiftoff(unittest.TestCase):
    def test_sim_ignition_to_liftoff(self):
        print("\nTesting ignition to liftoff function...")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')

            t_liftoff = sim_ignition_to_liftoff(past_flight.rocket, past_flight.environment, past_flight.launchpad)

            print(f"\tTime of liftoff: {t_liftoff} s")
            
            assert t_liftoff >= 0 # the 'or equal to' lets thrust curves that don't start at 0 pass, even though they shouldn't start at 0 if they're made properly

    def test_sim_ignition_to_liftoff_with_hold_down_force(self):
        print("\nTesting ignition to liftoff function with hold-down force...")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')
            past_flight.launchpad.hold_down_clamp_force = 500

            t_liftoff = sim_ignition_to_liftoff(past_flight.rocket, past_flight.environment, past_flight.launchpad)

            print(f"\tTime of liftoff with hold-down force: {t_liftoff} s")
            assert t_liftoff >= 0

    def test_sim_ignition_to_liftoff_with_hold_down_time(self):
        print("\nTesting ignition to liftoff function with hold-down time...")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')
            past_flight.launchpad.hold_down_clamp_release_time = 0.25

            t_liftoff = sim_ignition_to_liftoff(past_flight.rocket, past_flight.environment, past_flight.launchpad)

            print(f"\tTime of liftoff with hold-down time: {t_liftoff} s")
            assert t_liftoff >= 0

    def test_sim_ignition_to_liftoff_with_hold_down_force_and_time(self):
        print("\nTesting ignition to liftoff function with hold-down force and time...")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')
            past_flight.launchpad.hold_down_clamp_force = 1000
            past_flight.launchpad.hold_down_clamp_release_time = 2.0

            t_liftoff = sim_ignition_to_liftoff(past_flight.rocket, past_flight.environment, past_flight.launchpad)

            print(f"\tTime of liftoff with hold-down force and time: {t_liftoff} s")
            assert t_liftoff >= 0