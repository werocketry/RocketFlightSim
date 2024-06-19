# Import libraries
import sys
import os

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples')))
from . import helper_functions as hfunc
from . import constants as con

# TODO: see if Numba can speed up the simulation https://numba.pydata.org/

# Default timestep for the simulation
default_timestep = 0.02
""" Notes on timesteps:

The default for OpenRocket sims is 0.01s for the first while, and then somewhere between 0.02 and 0.05 for a while, and then 0.05 for most of the rest of the ascent. It simulates more complicated dynamics than we do

A timestep of 0.02s gives apogees a difference of a few feet for a 10k launch compared to using 0.001s. 0.001s can still be used for one-off sims, but when running many sims, 0.02s is better.
"""

# TODO consider splitting simulator into stages. Could be better for readability, but also for allowing more complex simulations with multiple stages, and going beyond the troposphere with different lapse rates, a different gravity model, and a different wind model. Could even use it for educational purposes like showing the importance of having a launch rail. Might also make it faster not having to store most variables during some stages (nothing stored at all before liftoff, no need to store angle to vertical at each timestep while on launch rail). 
# Flight simulation
def simulate_flight(rocket, launch_conditions, timestep=default_timestep):
    """
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
    launchpad_pressure = launch_conditions.launchpad_pressure
    launchpad_temp = launch_conditions.launchpad_temp
    L_launch_rail = launch_conditions.L_launch_rail
    launch_rail_elevation = launch_conditions.launch_rail_elevation
    launch_rail_direction = np.deg2rad(launch_conditions.launch_rail_direction)
    
    T_lapse_rate = launch_conditions.local_T_lapse_rate
    F_gravity = launch_conditions.local_gravity

    mean_wind_speed = launch_conditions.mean_wind_speed
    wind_heading = np.deg2rad(launch_conditions.wind_heading)
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # Initialize simulation variables
    time, height, airspeed, groundspeed, a_x, a_y, a_z, v_x, v_y, v_z, Ma, q = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    angle_to_vertical = np.deg2rad(90 - launch_rail_elevation)
    if angle_to_vertical == 0:
        angle_to_vertical = 0.0000001
        # TODO: find a better workaround

    # Calculate constants to be used in air density function, set initial air density
    multiplier = launchpad_pressure / (con.R_specific_air * pow(launchpad_temp, - F_gravity / (con.R_specific_air * T_lapse_rate)))
    exponent = - F_gravity / (con.R_specific_air * T_lapse_rate) - 1
    air_density = hfunc.air_density_optimized(launchpad_temp, multiplier, exponent)

    # Store the initial state of the rocket
    simulated_values = [
        [
            time, # 0
            height, # 0
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
                height, # 0
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
    effective_L_launch_rail = L_launch_rail - rocket.h_second_rail_button
    effective_h_launch_rail = effective_L_launch_rail * cos_rail_angle_to_vertical

    sin_launch_rail_direction = np.sin(launch_rail_direction)
    cos_launch_rail_direction = np.cos(launch_rail_direction)

    # Simulate flight from liftoff until the launch rail is cleared
    while height < effective_h_launch_rail:
        # Update environmental conditions based on height
        temperature = hfunc.temp_at_height(height, launchpad_temp, lapse_rate = T_lapse_rate)
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

        height += v_z * timestep

        # Append updated simulation values
        simulated_values.append(
            [
                time,
                height,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                launchpad_temp,
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
        temperature = hfunc.temp_at_height(height, launchpad_temp, lapse_rate = T_lapse_rate)
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

        height += v_z * timestep

        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = np.sqrt((v_x - 0.2*windspeed_x)**2 + (v_y - 0.2*windspeed_y)**2 + v_z**2)

        # New headings
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        # Append updated simulation values
        simulated_values.append(
            [
                time,
                height,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                launchpad_temp,
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
        temperature = hfunc.temp_at_height(height, launchpad_temp, lapse_rate = T_lapse_rate)
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

        height += v_z * timestep
        
        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)

        # New headings
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        # Append updated simulation values
        simulated_values.append(
            [
                time,
                height,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                launchpad_temp,
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
            "height",
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

    Args:
    - pre_brake_flight (DataFrame): A DataFrame containing the simulation results from the rocket's ascent until burnout. # TODO: change to a tuple of the dataset at the time to start the simulation with airbrakes. Maybe also sim from launch if not given
    - rocket (Rocket): An instance of the Rocket class.
    - launch_conditions (LaunchConditions): An instance of the LaunchConditions class.
    - airbrakes (Airbrakes): An instance of the Airbrakes class.
    - timestep (float, optional): The time increment for the simulation in seconds.

    Returns:
    - DataFrame: A DataFrame containing the simulation results from the rocket's post-burnout ascent with airbrakes deployed until apogee.
    """
    # Extract rocket parameters
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # Extract launch condition parameters
    launchpad_pressure = launch_conditions.launchpad_pressure
    launchpad_temp = launch_conditions.launchpad_temp

    T_lapse_rate = launch_conditions.local_T_lapse_rate
    F_gravity = launch_conditions.local_gravity

    mean_wind_speed = launch_conditions.mean_wind_speed
    wind_heading = np.deg2rad(launch_conditions.wind_heading)
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # Calculate constants to be used in air density function
    multiplier = launchpad_pressure / (con.R_specific_air * pow(launchpad_temp, - F_gravity / (con.R_specific_air * T_lapse_rate)))
    exponent = - F_gravity / (con.R_specific_air * T_lapse_rate) - 1

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
    height = pre_brake_flight["height"].iloc[-1]
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

        temperature = hfunc.temp_at_height(height, launchpad_temp, lapse_rate = T_lapse_rate)
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

        height += v_z * timestep

        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)

        # New headings
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        # Append updated simulation values
        simulated_values.append(
            [
                time,
                height,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                launchpad_temp,
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
            "height",
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

    Args:
    - initial_state_vector (list): A list containing the initial state of the rocket at the start of the airbrakes simulation. First index is height, second is v_x, third is v_y, fourth is v_z.
    - rocket (Rocket): An instance of the Rocket class.
    - launch_conditions (LaunchConditions): An instance of the LaunchConditions class.
    - airbrakes (Airbrakes): An instance of the Airbrakes class.
    - deployment_function (function): A function that takes the height of the rocket as an argument and returns the angle of the airbrakes deployment at that height in radians.
    - timestep (float, optional): The time increment for the simulation in seconds.

    Returns:
    - DataFrame: A DataFrame containing the simulation results from the rocket's post-burnout ascent with airbrakes deployed until apogee.
    """
    # Extract rocket parameters
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # Extract launch condition parameters
    launchpad_temp = launch_conditions.launchpad_temp
    launchpad_pressure = launch_conditions.launchpad_pressure

    T_lapse_rate = launch_conditions.local_T_lapse_rate
    F_gravity = launch_conditions.local_gravity

    mean_wind_speed = launch_conditions.mean_wind_speed
    wind_heading = np.deg2rad(launch_conditions.wind_heading)
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # Calculate constants to be used in air density function
    multiplier = launchpad_pressure / (con.R_specific_air * pow(launchpad_temp, - F_gravity / (con.R_specific_air * T_lapse_rate)))
    exponent = - F_gravity / (con.R_specific_air * T_lapse_rate) - 1

    # Extract airbrakes parameters
    Cd_brakes = airbrakes.Cd_brakes
    A_brakes = airbrakes.A_brakes
    # for efficiency, may be removed if/when the simulation is made more accurate by the cd of the brakes changing during the sim:
    A_Cd_brakes = A_brakes * Cd_brakes

    # Initialize simulation variables
    time = 0
    height = initial_state_vector[0]
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

        temperature = hfunc.temp_at_height(height, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)
        
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)

        deployment_angle = deployment_function(height)

        F_drag = q * (np.sin(deployment_angle) * A_Cd_brakes + Cd_A_rocket)

        # Update rocket's motion parameters
        a_x = -F_drag * np.sin(angle_to_vertical) / mass * np.sin(compass_heading)
        a_y = -F_drag * np.sin(angle_to_vertical) / mass * np.cos(compass_heading)
        a_z = -F_drag * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        height += v_z * timestep

        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)

        # New headings
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        simulated_values.append(
            [
                time,
                height,
                airspeed,
                groundspeed,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                launchpad_temp,
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
            "height",
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