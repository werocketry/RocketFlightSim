import sys
import os
from copy import deepcopy
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_stages_combined import flight_sim_ignition_to_apogee

from .test_configs import past_flights

class TestRFSAccuracy(unittest.TestCase):
    def test_rfs_accuracy(self):
        print("\nTesting accuracy of RFS compared to flight data...")

        for past_flight in deepcopy(past_flights):
            print(f'For rocket: {past_flight.name}')

            apogee_simulated = flight_sim_ignition_to_apogee(past_flight.rocket, past_flight.environment, past_flight.launchpad)[-1][3]
            apogee_actual = past_flight.apogee
            difference = apogee_simulated - apogee_actual
            proportional_difference = difference / apogee_actual
            print(f"\tSimulated apogee: {round(apogee_simulated,2)} m\n\tActual apogee: {round(apogee_actual,2)} m\n\tDifference: {round(difference,2)} m\n\tPercent difference: {round(proportional_difference*100,2)}%\n")

            assert np.abs(proportional_difference) < 0.1


            # TODO compare max simulated speed and acceleration to flight data