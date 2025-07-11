import numpy as np

from . import helper_functions as hfunc
from . import constants as con

def sim_coast(rocket, environment, initial_state_vector, stop_condition = 'apogee', stop_condition_value = None, timestep = con.default_timestep):
    """
    Simulate the coast phase of a rocket's flight until a specified stop condition.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    initial_state_vector : tuple
        A tuple detailing the initial state of the rocket. AAA
    stop_condition : str
        The condition that will stop the simulation. Must be 'apogee', 'impact', 'below_altitude' or 'after_delay'. Default is 'apogee'.
    stop_condition_value : float
        The value that the stop condition will be compared to. For 'below_altitude', this is the altitude in meters. For 'after_delay', this is the time in seconds.
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the kinematic state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, and a_z of the rocket at that time.
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

    if stop_condition_fn():
        raise ValueError(f"Stop condition '{stop_condition}' is already met at the start of the simulation.")

    simulated_states = []

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
        a_x = -F_drag * np.sin(angle_to_vertical) * np.sin(compass_heading) / mass
        a_y = -F_drag * np.sin(angle_to_vertical) * np.cos(compass_heading) / mass
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
        simulated_states.append(
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

    # interpolate to determine the exact state at the transition and replace the last state with that
    if len(simulated_states) >= 2:
        last_state = simulated_states[-1]
        second_last_state = simulated_states[-2]

        t1 = second_last_state[0]
        t2 = last_state[0]

        if stop_condition == 'apogee':
            # interpolate where v_z crosses zero
            v_z1 = second_last_state[6]
            v_z2 = last_state[6]
            t_interp = t1 - v_z1 * (t2 - t1) / (v_z2 - v_z1)
            fraction = (t_interp - t1) / (t2 - t1)
        elif stop_condition == 'impact' or stop_condition == 'below_altitude':
            # interpolate where z crosses zero
            z1 = second_last_state[3]
            z2 = last_state[3]
            target = 0 if stop_condition == 'impact' else stop_condition_value
            t_interp = t1 + (target - z1) * (t2 - t1) / (z2 - z1)
            fraction = (t_interp - t1) / (t2 - t1)
        elif stop_condition == 'after_delay':
            # interpolate where time crosses the stop time
            t_start = initial_state_vector[0]
            t_stop = t_start + stop_condition_value
            fraction = (t_stop - t1) / (t2 - t1)

        # interpolate all state components
        interpolated_state = tuple(
            second_last_state[i] + fraction * (last_state[i] - second_last_state[i])
            for i in range(len(last_state))
        )

        # replace the last simulated state with interpolated state
        simulated_states[-1] = interpolated_state

    return simulated_states