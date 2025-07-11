import numpy as np

from . import helper_functions as hfunc
from . import constants as con

# TODO more work on picking the default timestep

def sim_parachute(rocket, environment, initial_state_vector, parachute, stop_condition = 'landed', stop_condition_value = None, timestep = con.default_timestep * 2):
    """
    Simulate the flight of a rocket with a deployed parachute.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    initial_state_vector : tuple
        A tuple detailing the state of the rocket at AAA.
    parachute : Parachute
        An instance of the Parachute class.
    stop_condition : str, optional
        The condition that will stop the simulation. Must be 'landed', 'below_altitude', or 'after_delay'. Default is 'landed'.
    stop_condition_value : float, optional
        The value that the stop condition will be compared to. For 'below_altitude', this is the altitude in meters. For 'after_delay', this is the time in seconds. Default is None.
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples, each detailing the state of the rocket at a given time.
    
    Notes
    -----
    Simply assumes the parachute's drags acts in the opposite direction of the rocket's motion relative to the air.
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

    # unpack parachute variables
    Cd_A_parachute = parachute.Cd_A
    deploy_altitude = parachute.deploy_altitude
    deploy_delay = parachute.deploy_delay

    # determine if parachute should be deployed, and if delay is needed, simulate until that time
    simulated_states = []

    if not parachute.deploy_altitude and not parachute.deploy_delay:
        # unpack the initial state vector
        time, x, y, z, v_x, v_y, v_z = initial_state_vector
    elif parachute.deploy_altitude and not parachute.deploy_delay:
        if z < deploy_altitude:
            # unpack the initial state vector
            time, x, y, z, v_x, v_y, v_z = initial_state_vector
        else:
            from . import flight_sim_coast as sim_coast
            simulated_states = sim_coast.sim_coast(rocket, environment, initial_state_vector, stop_condition = 'below_altitude', stop_condition_value = deploy_altitude)
            time, x, y, z, v_x, v_y, v_z = simulated_states[-1][:7]
    elif not parachute.deploy_altitude and parachute.deploy_delay:
        from . import flight_sim_coast as sim_coast
        simulated_states = sim_coast.sim_coast(rocket, environment, initial_state_vector, stop_condition = 'after_delay', stop_condition_value = deploy_delay)
        time, x, y, z, v_x, v_y, v_z = simulated_states[-1][:7]
    else:
        # TODO implement 'both' and 'either' methods
        pass

    airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)
    unit_vx = (v_x - windspeed_x) / airspeed
    unit_vy = (v_y - windspeed_y) / airspeed
    unit_vz = v_z / airspeed

    # set stop condition logic
    if stop_condition == 'landed':
        def continue_while() -> bool:
            return z >= 0
    elif stop_condition == 'below_altitude':
        def continue_while() -> bool:
            return z >= stop_condition_value
    elif stop_condition == 'after_delay':
        def continue_while() -> bool:
            return time - initial_state_vector[0] <= stop_condition_value
    else:
        # TODO add a 'both' stop condition
        # TODO maybe add stop conditions for 'velocity' and 'acceleration', and change 'below_altitude' to 'altitude', with all positive values meaning 'below' and all negative values being 'above'
            # TODO have the user pass a function that takes in the current state and returns a boolean?
        raise ValueError("Invalid stop_condition. Must be AAA")

    # simulate descent under parachute
    while continue_while():
        # update air properties based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # calculate drag force
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        F_drag = q * Cd_A_parachute

        # update rocket's motion parameters
        a_x = - F_drag * unit_vx / mass
        a_y = - F_drag * unit_vy / mass
        a_z = (- F_drag * unit_vz / mass) - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        x += v_x * timestep
        y += v_y * timestep
        z += v_z * timestep

        # determine new headings
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)
        unit_vx = (v_x - windspeed_x) / airspeed
        unit_vy = (v_y - windspeed_y) / airspeed
        unit_vz = v_z / airspeed

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

    return simulated_states
# TODO after first implementation, have it determine the exact state (between timesteps) that the transition from chute to no chute occurs, and then again for the transition out of the function
    # TODO could I make a function for interpolating between states based on any transition condition? Then don't have to repeat it in every flight stage function