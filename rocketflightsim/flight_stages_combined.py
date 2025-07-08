# Import libraries
import numpy as np

from . import constants as con
default_timestep = con.default_timestep

from .flight_sim_ignition_to_liftoff import sim_ignition_to_liftoff
from .flight_sim_guided import sim_liftoff_to_rail_clearance
from .flight_sim_unguided_boost import sim_unguided_boost
from .flight_sim_coast import sim_coast
from .flight_sim_parachute import sim_parachute

def flight_sim_ignition_to_apogee(rocket, environment, launchpad, timestep=default_timestep):
    """
    Simulate the flight of a rocket from ignition to apogee given its specifications and launch conditions.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    launchpad : Launchpad
        An instance of the Launchpad class.
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the kinematic state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, and a_z of the rocket at that time.
    """
    flightpath = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Initial state vector (time, x, y, z, v_x, v_y, v_z, a_x, a_y, a_z)
    t_liftoff = sim_ignition_to_liftoff(rocket, environment, launchpad)
    flightpath.append((t_liftoff, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # append liftoff time to flightpath
    guided_flightpath = sim_liftoff_to_rail_clearance(rocket, environment, launchpad, t_liftoff, timestep)
    flightpath.extend(guided_flightpath)  # append the last state vector to flightpath
    flightpath_to_burnout = sim_unguided_boost(rocket, environment, guided_flightpath[-1], timestep)
    flightpath.extend(flightpath_to_burnout)  # combine the flight paths
    flightpath_to_apogee = sim_coast(rocket, environment, flightpath[-1], timestep=timestep)
    flightpath.extend(flightpath_to_apogee)  # combine the flight paths

    return flightpath

def flight_sim_ignition_to_landing(rocket, environment, launchpad, parachutes_and_conditions, timestep=default_timestep):
    """
    Simulate the flight of a rocket from ignition to landing under a parachute given its specifications and launch conditions.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    launchpad : Launchpad
        An instance of the Launchpad class.
    parachutes_and_conditions : list
        A list of tuples, each containing an instance of the Parachute class and the conditions upon which that parachute stops controlling the flight. Takes the form (parachute, stop_condition, stop_condition_value).
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the kinematic state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, and a_z of the rocket at that time.
    """
    flightpath = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Initial state vector (time, x, y, z, v_x, v_y, v_z, a_x, a_y, a_z)
    t_liftoff = sim_ignition_to_liftoff(rocket, environment, launchpad)
    flightpath.append((t_liftoff, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # append liftoff time to flightpath
    guided_flightpath = sim_liftoff_to_rail_clearance(rocket, environment, launchpad, t_liftoff, timestep)
    flightpath.extend(guided_flightpath)  # append the last state vector to flightpath
    flightpath_to_burnout = sim_unguided_boost(rocket, environment, guided_flightpath[-1], timestep)
    flightpath.extend(flightpath_to_burnout)  # combine the flight paths
    flightpath_to_apogee = sim_coast(rocket, environment, flightpath[-1], timestep=timestep)
    for parachute, stop_condition, stop_condition_value in parachutes_and_conditions:
        flightpath_with_chute = sim_parachute(rocket, environment, flightpath_to_apogee[-1], parachute, stop_condition=stop_condition, stop_condition_value=stop_condition_value, timestep=timestep)
        flightpath.extend(flightpath_with_chute)

    return flightpath

def flight_sim_ballistic_recovery(rocket, environment, launchpad, timestep=default_timestep):
    """
    Simulate the flight of a rocket that does not deploy a parachute and instead falls ballistically back to the ground.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    launchpad : Launchpad
        An instance of the Launchpad class.
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the kinematic state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, and a_z of the rocket at that time.
    """
    flightpath = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Initial state vector (time, x, y, z, v_x, v_y, v_z, a_x, a_y, a_z)
    t_liftoff = sim_ignition_to_liftoff(rocket, environment, launchpad)
    flightpath.append((t_liftoff, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # append liftoff time to flightpath
    guided_flightpath = sim_liftoff_to_rail_clearance(rocket, environment, launchpad, t_liftoff, timestep)
    flightpath.extend(guided_flightpath)  # append the last state vector to flightpath
    flightpath_to_burnout = sim_unguided_boost(rocket, environment, guided_flightpath[-1], timestep)
    flightpath.extend(flightpath_to_burnout)  # combine the flight paths
    flightpath_to_impact = sim_coast(rocket, environment, flightpath[-1], stop_condition='impact', timestep=timestep)
    flightpath.extend(flightpath_to_impact)  # combine the flight paths

    return flightpath
