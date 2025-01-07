import numpy as np

from . import helper_functions as hfunc
from . import constants as con

def sim_coast_phase(rocket, environment, initial_state_vector, stop_condition, stop_condition_value, timestep = con.default_timestep):
    """
    Simulate the coast phase of a rocket's flight until a specified stop condition.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    initial_state_vector : tuple
        A tuple detailing the state of the rocket at the start of coasting. AAA
    stop_condition : str
        The condition that will stop the simulation. Must be 'apogee', 'impact', 'below_altitude' or 'after_delay'.
    stop_condition_value : float
        The value that the stop condition will be compared to. For 'below_altitude', this is the altitude in meters. For 'after_delay', this is the time in seconds.
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, and a_z of the rocket at that time.
    """

    # unpack environmental variables
    launchpad_temp = environment.launchpad_temp

    T_lapse_rate = environment.local_T_lapse_rate
    F_gravity = environment.local_gravity

    multiplier = environment.density_multiplier
    exponent = environment.density_exponent

    mean_wind_speed = environment.mean_wind_speed
    wind_heading = environment.wind_heading
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # unpack rocket variables
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # unpack simulation variables
    time = initial_state_vector[0]
    x = initial_state_vector[1]
    y = initial_state_vector[2]
    z = initial_state_vector[3]
    v_x = initial_state_vector[4]
    v_y = initial_state_vector[5]
    v_z = initial_state_vector[6]
    groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2) # will be used for AoA
    airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)

    compass_heading = np.arctan(v_x / v_y)
    angle_to_vertical = np.arccos(v_z / airspeed)

    # set stop condition
    if stop_condition == 'apogee':
        stop_condition_fn = lambda: v_z <= 0
    elif stop_condition == 'impact':
        stop_condition_fn = lambda: z <= 0
    elif stop_condition == 'below_altitude':
        stop_condition_fn = lambda: z <= stop_condition_value
    elif stop_condition == 'after_delay':
        stop_condition_fn = lambda: time - initial_state_vector[0] >= stop_condition_value

    # simulate flight from launch rail clearance until motor burnout
    simulated_values = []

    while not stop_condition_fn():
        # update air properties based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # calculate drag force
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        F_drag = q * Cd_A_rocket

        # update rocket's motion parameters
        a_x = -F_drag * np.sin(angle_to_vertical) / mass * np.sin(compass_heading)
        a_y = -F_drag * np.sin(angle_to_vertical) / mass * np.cos(compass_heading)
        a_z = -F_drag * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        x += v_x * timestep
        y += v_y * timestep
        z += v_z * timestep

        # determine new headings
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        time += timestep

        # append updated simulation values
        simulated_values.append(
            (
                time,
                x,
                y,
                z,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
            )
        )

    # TODO Interpolate to determine the exact state (between timesteps) at the transition and replace the last state with that

    return simulated_values

def sim_coast_to_apogee(rocket, environment, initial_state_vector, timestep = con.default_timestep):
    """
    Simulate the coast phase of a rocket's flight until apogee.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    initial_state_vector : tuple
        A tuple detailing the state of the rocket at the start of the coasting phase. AAA
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, and a_z of the rocket at that time.
    
    Notes
    -----
    The simulation is the exact same as the sim_coast simulation with the stop condition set to 'apogee'.
    """

    # unpack environmental variables
    launchpad_temp = environment.launchpad_temp

    T_lapse_rate = environment.local_T_lapse_rate
    F_gravity = environment.local_gravity

    multiplier = environment.density_multiplier
    exponent = environment.density_exponent

    mean_wind_speed = environment.mean_wind_speed
    wind_heading = environment.wind_heading
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # unpack rocket variables
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # unpack simulation variables
    time = initial_state_vector[0]
    x = initial_state_vector[1]
    y = initial_state_vector[2]
    z = initial_state_vector[3]
    v_x = initial_state_vector[4]
    v_y = initial_state_vector[5]
    v_z = initial_state_vector[6]
    groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2) # will be used for AoA
    airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)

    compass_heading = np.arctan(v_x / v_y)
    angle_to_vertical = np.arccos(v_z / airspeed)

    # simulate flight from launch rail clearance until motor burnout
    simulated_values = []

    while v_z > 0:
        # update air properties based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # calculate drag force
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        F_drag = q * Cd_A_rocket

        # update rocket's motion parameters
        a_x = -F_drag * np.sin(angle_to_vertical) / mass * np.sin(compass_heading)
        a_y = -F_drag * np.sin(angle_to_vertical) / mass * np.cos(compass_heading)
        a_z = -F_drag * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        x += v_x * timestep
        y += v_y * timestep
        z += v_z * timestep

        # determine new headings
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        time += timestep

        # append updated simulation values
        simulated_values.append(
            (
                time,
                x,
                y,
                z,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
            )
        )

    # Interpolate to find the exact state at apogee
    last_state = simulated_values[-1]
    second_last_state = simulated_values[-2]

    t1, v_z1 = second_last_state[0], second_last_state[6]
    t2, v_z2 = last_state[0], last_state[6]

    # Linear interpolation to find the time at which v_z reaches zero (apogee)
    t_apogee = t1 - v_z1 * (t2 - t1) / (v_z2 - v_z1)
    fraction = (t_apogee - t1) / (t2 - t1)

    # Interpolate all state components to find the state at apogee
    interpolated_state = tuple(
        second_last_state[i] + fraction * (last_state[i] - second_last_state[i])
        for i in range(len(last_state))
    )

    # Replace the last state with the interpolated state
    simulated_values[-1] = interpolated_state

    return simulated_values