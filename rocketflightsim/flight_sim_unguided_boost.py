import numpy as np

from . import helper_functions as hfunc
from . import constants as con
# TODO merge this with the coast sim functions into an unguided flight sim file?
def sim_unguided_boost(rocket, environment, initial_state_vector, timestep = con.default_timestep):
    """
    Simulate the flight of a rocket from the moment of launch rail clearance until motor burnout.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    initial_state_vector : tuple
        A tuple detailing the state of the rocket at launch rail clearance. AAA
    timestep : float
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
    dry_mass = rocket.dry_mass
    fuel_mass_lookup = rocket.motor.fuel_mass_curve
    engine_thrust_lookup = rocket.motor.thrust_curve
    Cd_A_rocket_fn = rocket.Cd_A_rocket
    burnout_time = rocket.motor.burn_time

    # unpack simulation variables
    time = initial_state_vector[0]
    x = initial_state_vector[1]
    y = initial_state_vector[2]
    z = initial_state_vector[3]
    v_x = initial_state_vector[4]
    v_y = initial_state_vector[5]
    v_z = initial_state_vector[6]
    groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2) # for comparing to airspeed to get AoA at clearance, eventually make a better way to have it fly with a small AoA for the first little bit
    airspeed = np.sqrt((v_x - 0.2*windspeed_x)**2 + (v_y - 0.2*windspeed_y)**2 + v_z**2)

    compass_heading = np.arctan(v_x / v_y)
    angle_to_vertical = np.arccos(v_z / airspeed)

    # simulate flight from launch rail clearance until motor burnout
    simulated_states = []

    while time < burnout_time:
        # update air properties based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # calculate drag force
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        F_drag = q * Cd_A_rocket

        # update rocket's motion parameters
        mass = hfunc.mass_at_time(time, dry_mass, fuel_mass_lookup)
        thrust = hfunc.thrust_at_time(time, engine_thrust_lookup)

        a_x = (thrust - F_drag) * np.sin(angle_to_vertical) * np.sin(compass_heading) / mass
        a_y = (thrust - F_drag) * np.sin(angle_to_vertical) * np.cos(compass_heading) / mass
        a_z = (thrust - F_drag) * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        x += v_x * timestep
        y += v_y * timestep
        z += v_z * timestep

        # determine new headings
        airspeed = np.sqrt((v_x - 0.2*windspeed_x)**2 + (v_y - 0.2*windspeed_y)**2 + v_z**2)
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

    # interpolate to find the exact state at burnout time
    last_state = simulated_states[-1]
    second_last_state = simulated_states[-2]

    # linear interpolation between the last two states
    time_diff = last_state[0] - second_last_state[0]
    fraction = (burnout_time - second_last_state[0]) / time_diff

    interpolated_state = tuple(
        second_last_state[i] + fraction * (last_state[i] - second_last_state[i])
        for i in range(len(last_state))
    )

    # replace the last state with the interpolated state
    simulated_states[-1] = interpolated_state

    return simulated_states