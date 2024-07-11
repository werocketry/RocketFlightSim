import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rocketflightsim.flight_simulation import simulate_flight

from .test_configs import past_flights

class TestNewSimulation(unittest.TestCase):
    def test_new_simulation(self):
        print("Testing new simulation")
        from rocketflightsim.flight_simulation import flight_sim_ignition_to_liftoff, flight_sim_liftoff_to_rail_clearance, flight_sim_rail_clearance_to_burnout, flight_sim_burnout_to_apogee, flight_sim_ignition_to_apogee

        for past_flight in past_flights:
            print(f'For rocket: {past_flight.name}')

            new_time_to_liftoff = flight_sim_ignition_to_liftoff(past_flight.rocket, past_flight.launch_conditions)

            print(f'With new liftoff function, time to liftoff is:\n{new_time_to_liftoff}')
            print(f'Old time to liftoff is:')
            dataset, liftoff_index, launch_rail_cleared_index, burnout_index, apogee_index = simulate_flight(rocket=past_flight.rocket, launch_conditions=past_flight.launch_conditions, timestep=0.001)

            new_rail_clearance_function_states = flight_sim_liftoff_to_rail_clearance(past_flight.rocket, past_flight.launch_conditions, new_time_to_liftoff, 0.001)

            print(f"With new liftoff to rail clearance function, the state at rail clearance is:\n {new_rail_clearance_function_states[-1]}")

            new_till_burnout_function_states = flight_sim_rail_clearance_to_burnout(past_flight.rocket, past_flight.launch_conditions, new_rail_clearance_function_states[-1], 0.001)
            
            print(f"With new rail clearance to burnout function, the state at burnout is:\n {new_till_burnout_function_states[-1]}")

            new_till_apogee_function_states = flight_sim_burnout_to_apogee(past_flight.rocket, past_flight.launch_conditions, new_till_burnout_function_states[-1], 0.001)

            print(f"With new to apogee function, the state at apogee is:\n {new_till_apogee_function_states[-1]}")

            new_combined_functions_apogee_state = flight_sim_ignition_to_apogee(past_flight.rocket, past_flight.launch_conditions, 0.001)

            print(f"With new combined functions, the state at apogee is:\n {new_combined_functions_apogee_state}")
            print('\n')