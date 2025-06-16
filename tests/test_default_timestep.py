import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_stages_combined import simulate_flight, simulate_airbrakes_flight_max_deployment

from .test_configs import past_flights
from .test_configs import Juno3_rocket, Juno3_environment

class TestDefaultTimestep(unittest.TestCase):
     def test_default_timestep(self):
            print("Testing default timestep")
            
            # TODO test to verify slight changes from the default timestep don't have a significant effect on the simulation results
# from flight simulation file, used to pick the default timestep:

# run a couple hundred different timesteps in logspace between 0.001 and 0.1 to see how it changes to help pick a good timestep
"""apogees = []
for timestep in np.logspace(-3, -1, 200):
    dataset, liftoff_index, launch_rail_cleared_index, burnout_index, apogee_index = simulate_flight(rocket=Juno3_rocket, timestep=timestep)
    ascent, time_of_max_deployment = simulate_airbrakes_flight_max_deployment(dataset.iloc[:burnout_index].copy(), rocket=Juno3_rocket, launch_conditions=Juno3_launch_conditions, timestep=0.001)
    apogees.append(ascent["z"].iloc[-1]*3.28084)
    print(len(apogees))
# plot them
import matplotlib.pyplot as plt
plt.plot(np.logspace(-3, -1, 200), apogees)
plt.xscale("log")
plt.xlabel("Timestep (s)")
plt.ylabel("Apogee (ft)")
plt.title("Apogee vs Timestep")
plt.show()"""

# TODO add a test to verify that the simulation doesn't take too long to run