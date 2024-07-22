import numpy as np

from . import helper_functions as hfunc
from . import constants as con

def flight_sim_burnout_to_apogee(rocket, launch_conditions, initial_state_vector, timestep = con.default_timestep):
    """
    Simulate a rocket's flight from the time of motor burnout until apogee.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    launch_conditions : LaunchConditions
        An instance of the LaunchConditions class.
    initial_state_vector : tuple
        A tuple detailing the state of the rocket at burnout. AAA
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        aaa
    """
    # TODO maybe after first implementation, have it determine the exact state (between timesteps) at apogee and replace the last state with that

    # unpack environmental variables
    launchpad_temp = launch_conditions.launchpad_temp

    T_lapse_rate = launch_conditions.local_T_lapse_rate
    F_gravity = launch_conditions.local_gravity

    multiplier = launch_conditions.density_multiplier
    exponent = launch_conditions.density_exponent

    mean_wind_speed = launch_conditions.mean_wind_speed
    wind_heading = launch_conditions.wind_heading
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # unpack rocket variables
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # unpack simulation variables
    time = initial_state_vector[0]
    z = initial_state_vector[1]
    v_x = initial_state_vector[2]
    v_y = initial_state_vector[3]
    v_z = initial_state_vector[4]
    groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2) # will be used for AoA
    airspeed = np.sqrt((v_x - 0.2*windspeed_x)**2 + (v_y - 0.2*windspeed_y)**2 + v_z**2)

    compass_heading = launch_conditions.launch_rail_direction
    angle_to_vertical = launch_conditions.angle_to_vertical

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

        # add x and y after finishing implementation and comparing speed to old version
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
                # x,
                # y,
                z,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
            )
        )

    return simulated_values