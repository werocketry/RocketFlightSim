# Import libraries
import sys
import os

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples')))
from . import helper_functions as hfunc
from . import constants as con

# Default timestep for the simulation
default_timestep = con.default_timestep

# TODO improvements to overall simulator:
"""
    - make it easier to do multi-stage rockets? Currently just chain sim_unguided_boost for each additional stage with new rocket and motor objects for additional stages
    - see if Numba can speed up the simulation https://numba.pydata.org/
    - consider using different default timesteps for different stages
        - consider a full-on adaptive timestep system like ork has
    - speed test using np.linalg.norm vs squaring and square rooting
"""

# TODO split simulator into stages. better for readability, but also for allowing more complex simulations with multiple stages, and going beyond the troposphere with different lapse rates, a different gravity model, and a different wind model. Could even use it for educational purposes like showing the importance of having a launch rail. Also makes it faster not having to store most variables during some stages (nothing stored at all before liftoff, no need to store angle to vertical at each timestep while on launch rail), and not having to re-do significant parts of the simulation when running it multiple times (if looking at how varying wind affects the flightpath, can just sim to launch rail clearance once). Could also make a few things faster and more precise like between ignition and liftoff, instead of timestepping, could solve for the exact time of liftoff.

from .flight_sim_ignition_to_liftoff import sim_ignition_to_liftoff
from .flight_sim_guided import sim_liftoff_to_rail_clearance
from .flight_sim_unguided_boost import sim_unguided_boost
from .flight_sim_coast import sim_coast_phase, sim_coast_to_apogee

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
        aaa
    """
    t_liftoff = sim_ignition_to_liftoff(rocket, environment, launchpad)

    state_at_rail_clearance = sim_liftoff_to_rail_clearance(rocket, environment, launchpad, t_liftoff, timestep) [-1]

    state_at_burnout = sim_unguided_boost(rocket, environment, state_at_rail_clearance, timestep)[-1]

    state_at_apogee = sim_coast_to_apogee(rocket, environment, state_at_burnout, timestep)[-1]

    return state_at_apogee

""" TODO combining them. and likely some kind of flagging specific times as key events (needed? at least some of them can be gotten from the launch conditions like burnout (from time), liftoff (first non-zero height), and rail clearance (from rail height))

key events:
    ignition
        t = 0
    liftoff
        first v_z > 0
    max g from motor burn
        a_max
            can be solved for by looking at the thrust curve and mass curve like done in sim_ignition_to_liftoff
    rail clearance
        first z > effective_rail_height
    max q
        air_density * v ** 2 is max
    max speed and Ma
        v = v_max
    burnout
        from time and motor class
    apogee
        last simmed state
"""

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
        aaa
    """
    t_liftoff = sim_ignition_to_liftoff(rocket, environment, launchpad)

    state_at_rail_clearance = sim_liftoff_to_rail_clearance(rocket, environment, launchpad, t_liftoff, timestep) [-1]

    state_at_burnout = sim_unguided_boost(rocket, environment, state_at_rail_clearance, timestep)[-1]

    state_at_impact = sim_coast_phase(rocket, environment, state_at_burnout, 'impact')[-1]

    return state_at_impact

# TODO: replace all old combined functions

# Flight simulation
def simulate_flight(rocket, launch_conditions, timestep=default_timestep):
    """ OLD FUNCTION
    Simulate the flight of a rocket until its apogee given its specifications and launch conditions.

    Args:
    - rocket (Rocket): An instance of the Rocket class.
    - launch_conditions (LaunchConditions): An instance of the LaunchConditions class.
    - timestep (float, optional): The time increment for the simulation in seconds.

    Returns:
    - tuple: A tuple containing the dataset of simulation results and indices of key flight events.
    """

    # Initialize rocket parameters and launch conditions
    dry_mass = rocket.dry_mass
    fuel_mass_lookup = rocket.motor.fuel_mass_curve
    engine_thrust_lookup = rocket.motor.thrust_curve
    Cd_A_rocket_fn = rocket.Cd_A_rocket
    burnout_time = rocket.motor.burn_time

    # Extract launch condition parameters
    launchpad_temp = launch_conditions.launchpad_temp

    rail_length = launch_conditions.rail_length
    angle_to_vertical = launch_conditions.angle_to_vertical
    launch_rail_direction = launch_conditions.launch_rail_direction
    
    T_lapse_rate = launch_conditions.local_T_lapse_rate
    F_gravity = launch_conditions.local_gravity

    mean_wind_speed = launch_conditions.mean_wind_speed
    wind_heading = launch_conditions.wind_heading
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # Initialize simulation variables
    time, z, airspeed, groundspeed, v_x, v_y, v_z, a_x, a_y, a_z, Ma, q = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    # Calculate constants to be used in air density function, set initial air density
    multiplier = launch_conditions.density_multiplier
    exponent = launch_conditions.density_exponent
    air_density = hfunc.air_density_optimized(launchpad_temp, multiplier, exponent)

    # Store the initial state of the rocket
    simulated_values = [
        [
            time, # 0
            z, # 0
            airspeed, # 0
            groundspeed, # 0
            v_x, # 0
            v_y, # 0
            v_z, # 0
            a_x, # 0
            a_y, # 0
            a_z, # 0
            launchpad_temp,
            air_density,
            q, # 0
            Ma, # 0
            angle_to_vertical,
        ]
    ]

    # Calculate trigonometric ratios on the launch rail
    cos_rail_angle_to_vertical = np.cos(angle_to_vertical)
    sin_rail_angle_to_vertical = np.sin(angle_to_vertical)

    # Simulate motor burn until liftoff
    takeoff_thrust = F_gravity * cos_rail_angle_to_vertical
    while (
        hfunc.thrust_at_time(time, engine_thrust_lookup)
        / hfunc.mass_at_time(time, dry_mass, fuel_mass_lookup)
        <= takeoff_thrust
    ):
        time += timestep
        # Append simulation values for each timestep
        simulated_values.append(
            [
                time,
                z, # 0
                airspeed, # 0
                groundspeed, # 0
                v_x, # 0
                v_y, # 0
                v_z, # 0
                a_x, # 0
                a_y, # 0
                a_z, # 0
                launchpad_temp,
                air_density,
                q, # 0
                Ma, # 0
                angle_to_vertical,
            ]
        )

    liftoff_index = len(simulated_values)

    # Liftoff until launch rail cleared
    time += timestep
    effective_rail_length = rail_length - rocket.h_second_rail_button
    effective_rail_height = effective_rail_length * cos_rail_angle_to_vertical

    sin_launch_rail_direction = np.sin(launch_rail_direction)
    cos_launch_rail_direction = np.cos(launch_rail_direction)

    # Simulate flight from liftoff until the launch rail is cleared
    while z < effective_rail_height:
        # Update environmental conditions based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # Calculate Mach number, drag coefficient, and forces
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        F_drag = q * Cd_A_rocket

        # Update rocket's motion parameters
        mass = hfunc.mass_at_time(time, dry_mass, fuel_mass_lookup)
        thrust = hfunc.thrust_at_time(time, engine_thrust_lookup)
        a_rail = (thrust - F_drag) / mass - F_gravity * cos_rail_angle_to_vertical
        
        a_x = a_rail * sin_rail_angle_to_vertical * sin_launch_rail_direction
        a_y = a_rail * sin_rail_angle_to_vertical * cos_launch_rail_direction
        a_z = a_rail * cos_rail_angle_to_vertical

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = groundspeed

        z += v_z * timestep

        # Append updated simulation values
        simulated_values.append(
            [
                time,
                z,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                temperature,
                air_density,
                q,
                Ma,
                angle_to_vertical,
            ]
        )
        time += timestep

    compass_heading = np.arctan(v_x / v_y)
    launch_rail_cleared_index = len(simulated_values)

    # Flight from launch rail cleared until burnout
    while time < burnout_time:
        # Update environmental conditions based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # Calculate Mach number, Drag coefficient, and Forces
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        F_drag = q * Cd_A_rocket

        # Update rocket's motion parameters
        mass = hfunc.mass_at_time(time, dry_mass, fuel_mass_lookup)
        thrust = hfunc.thrust_at_time(time, engine_thrust_lookup)
        
        a_x = (thrust - F_drag) * np.sin(angle_to_vertical) / mass * (np.sin(compass_heading))
        a_y = (thrust - F_drag) * np.sin(angle_to_vertical) / mass * (np.cos(compass_heading))
        a_z = (thrust - F_drag) * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        z += v_z * timestep

        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = np.sqrt((v_x - 0.2*windspeed_x)**2 + (v_y - 0.2*windspeed_y)**2 + v_z**2)

        # New headings
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        # Append updated simulation values
        simulated_values.append(
            [
                time,
                z,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                temperature,
                air_density,
                q,
                Ma,
                angle_to_vertical,
            ]
        )

        time += timestep

    burnout_index = len(simulated_values)

    # Flight from burnout to apogee
    mass = dry_mass

    while v_z > 0:
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # Calculate Mach number, Drag coefficient, and Forces
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        F_drag = q * Cd_A_rocket

        # Update rocket's motion parameters
        a_x = -F_drag * np.sin(angle_to_vertical) / mass * np.sin(compass_heading)
        a_y = -F_drag * np.sin(angle_to_vertical) / mass * np.cos(compass_heading)
        a_z = -F_drag * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        z += v_z * timestep
        
        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)

        # New headings
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        # Append updated simulation values
        simulated_values.append(
            [
                time,
                z,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                temperature,
                air_density,
                q,
                Ma,
                angle_to_vertical,
            ]
        )

        time += timestep

    # Mark the index at apogee
    apogee_index = len(simulated_values)
    simulated_values[-1][-1] = simulated_values[-2][-1]

    # Convert the list of simulation values to a DataFrame for easier analysis and visualization
    dataset = pd.DataFrame(
        simulated_values,
        columns=[
            "time",
            "z",
            "airspeed",
            "groundspeed",
            "v_x",
            "v_y",
            "v_z",
            "a_x",
            "a_y",
            "a_z",
            "temperature",
            "air_density",
            "q",
            "Ma",
            "angle_to_vertical",
        ],
    )

    return (
        dataset,
        liftoff_index,
        launch_rail_cleared_index,
        burnout_index,
        apogee_index
    )

# Flight simulation with airbrakes - max deployment
def simulate_airbrakes_flight_max_deployment(pre_brake_flight, rocket, launch_conditions, airbrakes, timestep = default_timestep):
    """
    Simulate the flight of a rocket during its post-burnout ascent with airbrakes deployed until apogee, given its specifications and environmental conditions.

    Args
    ----
    - pre_brake_flight (DataFrame): A DataFrame containing the simulation results from the rocket's ascent until burnout.
    - rocket (Rocket): An instance of the Rocket class.
    - launch_conditions (LaunchConditions): An instance of the LaunchConditions class.
    - airbrakes (Airbrakes): An instance of the Airbrakes class.
    - timestep (float, optional): The time increment for the simulation in seconds.

    Returns
    -------
    - DataFrame: A DataFrame containing the simulation results from the rocket's post-burnout ascent with airbrakes deployed until apogee.
    """
    # Extract rocket parameters
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # Extract launch condition parameters
    launchpad_temp = launch_conditions.launchpad_temp

    T_lapse_rate = launch_conditions.local_T_lapse_rate
    F_gravity = launch_conditions.local_gravity

    mean_wind_speed = launch_conditions.mean_wind_speed
    wind_heading = launch_conditions.wind_heading
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # Calculate constants to be used in air density function
    multiplier = launch_conditions.density_multiplier
    exponent = launch_conditions.density_exponent

    # Extract airbrakes parameters
    Cd_brakes = airbrakes.Cd_brakes
    A_brakes = airbrakes.A_brakes
    # for efficiency, may be removed if/when the simulation is made more accurate by the cd of the brakes changing during the sim:
    A_Cd_brakes = A_brakes * Cd_brakes

    max_deployment_angle = np.deg2rad(airbrakes.max_deployment_angle)
    max_deployment_rate = np.deg2rad(airbrakes.max_deployment_rate)
    pre_brake_flight["deployment_angle"] = 0

    # Initialize simulation variables
    time = pre_brake_flight["time"].iloc[-1]
    z = pre_brake_flight["z"].iloc[-1]
    airspeed = pre_brake_flight["airspeed"].iloc[-1]
    v_x = pre_brake_flight["v_x"].iloc[-1]
    v_y = pre_brake_flight["v_y"].iloc[-1]
    v_z = pre_brake_flight["v_z"].iloc[-1]
    
    compass_heading = np.arctan(v_x / v_y)
    angle_to_vertical = np.arccos(v_z / airspeed)

    deployment_angle = 0

    simulated_values = []
    while v_z > 0:
        time += timestep

        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)
        
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)

        deployment_angle = min(max_deployment_angle, deployment_angle + max_deployment_rate * timestep)

        F_drag = q * (np.sin(deployment_angle) * A_Cd_brakes + Cd_A_rocket)

        # Update rocket's motion parameters
        a_x = -F_drag * np.sin(angle_to_vertical) / mass * np.sin(compass_heading)
        a_y = -F_drag * np.sin(angle_to_vertical) / mass * np.cos(compass_heading)
        a_z = -F_drag * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        z += v_z * timestep

        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)

        # New headings
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        # Append updated simulation values
        simulated_values.append(
            [
                time,
                z,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                temperature,
                air_density,
                q,
                Ma,
                angle_to_vertical,
                deployment_angle,
            ]
        )

    simulated_values[-1][11] = simulated_values[-2][11]

    airbrakes_ascent = pd.DataFrame(
        simulated_values,
        columns=[
            "time",
            "z",
            "airspeed",
            "groundspeed",
            "v_x",
            "v_y",
            "v_z",
            "a_x",
            "a_y",
            "a_z",
            "temperature",
            "air_density",
            "q",
            "Ma",
            "angle_to_vertical",
            "deployment_angle",
        ],
    )

    return airbrakes_ascent

# Flight simulation with airbrakes - deployed as a function of height
def simulate_airbrakes_flight_deployment_function_of_height(initial_state_vector, rocket, launch_conditions, airbrakes, deployment_function, timestep = default_timestep):
    """
    Simulate the flight of a rocket during its post-burnout ascent with airbrakes deployed according to a supplied function of height.

    Args
    ----
    - initial_state_vector (list): A list containing the initial state of the rocket at the start of the airbrakes simulation. First index is z, second is v_x, third is v_y, fourth is v_z.
    - rocket (Rocket): An instance of the Rocket class.
    - launch_conditions (LaunchConditions): An instance of the LaunchConditions class.
    - airbrakes (Airbrakes): An instance of the Airbrakes class.
    - deployment_function (function): A function that takes the height of the rocket as an argument and returns the angle of the airbrakes deployment at that height in radians.
    - timestep (float, optional): The time increment for the simulation in seconds.

    Returns
    -------
    - DataFrame: A DataFrame containing the simulation results from the rocket's post-burnout ascent with airbrakes deployed until apogee.
    """
    # Extract rocket parameters
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # Extract launch condition parameters
    launchpad_temp = launch_conditions.launchpad_temp

    T_lapse_rate = launch_conditions.local_T_lapse_rate
    F_gravity = launch_conditions.local_gravity

    mean_wind_speed = launch_conditions.mean_wind_speed
    wind_heading = launch_conditions.wind_heading
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # Calculate constants to be used in air density function
    multiplier = launch_conditions.density_multiplier
    exponent = launch_conditions.density_exponent

    # Extract airbrakes parameters
    Cd_brakes = airbrakes.Cd_brakes
    A_brakes = airbrakes.A_brakes
    # for efficiency, may be removed if/when the simulation is made more accurate by the cd of the brakes changing during the sim:
    A_Cd_brakes = A_brakes * Cd_brakes

    # Initialize simulation variables
    time = 0
    z = initial_state_vector[0]
    v_x = initial_state_vector[1]
    v_y = initial_state_vector[2]
    v_z = initial_state_vector[3]
    airspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)

    compass_heading = np.arctan(v_x / v_y)
    angle_to_vertical = np.arccos(v_z / airspeed)

    deployment_angle = 0

    simulated_values = []
    while v_z > 0:
        time += timestep

        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)
        
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)

        deployment_angle = deployment_function(z)

        F_drag = q * (np.sin(deployment_angle) * A_Cd_brakes + Cd_A_rocket)

        # Update rocket's motion parameters
        a_x = -F_drag * np.sin(angle_to_vertical) / mass * np.sin(compass_heading)
        a_y = -F_drag * np.sin(angle_to_vertical) / mass * np.cos(compass_heading)
        a_z = -F_drag * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        z += v_z * timestep

        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)

        # New headings
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        simulated_values.append(
            [
                time,
                z,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                temperature,
                air_density,
                q,
                Ma,
                angle_to_vertical,
                deployment_angle,
            ]
        )

    # simulated_values[-1][11] = simulated_values[-2][11]

    airbrakes_ascent = pd.DataFrame(
        simulated_values,
        columns=[
            "time",
            "z",
            "airspeed",
            "groundspeed",
            "v_x",
            "v_y",
            "v_z",
            "a_x",
            "a_y",
            "a_z",
            "temperature",
            "air_density",
            "q",
            "Ma",
            "angle_to_vertical",
            "deployment_angle",
        ],
    )
    
    return airbrakes_ascent