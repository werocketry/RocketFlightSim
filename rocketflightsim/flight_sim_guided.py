import numpy as np

from . import helper_functions as hfunc
from . import constants as con

def sim_liftoff_to_rail_clearance(rocket, environment, launchpad, t_liftoff, timestep = con.default_timestep):
    """
    Simulate the flight of a rocket on a launch rail from the time of liftoff unitl the moment the rocket clears the rail.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    launchpad : Launchpad
        An instance of the Launchpad class.
    t_liftoff : float
        Time after ignition at which the rocket lifts off in seconds.
    timestep : float
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the kinematic state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, and a_z of the rocket at that time.

    Notes
    -----
    This could be done in 1 dimension to save computation time, given the change in air properties over the length of the rail is negligible. Further, if the distance along the rail was taken as height - which it effectively is given most launch angles are close to vertical - accounting for the change in air properties that way would mean an even more negligeable difference compared to the real properties. The 1D motion could then be converted to 3D motion after the rocket has cleared the rail, given the location at the rail exit is determined by the (effective) length of the rail and the direction it is pointed in. For the sake of consistency, 3D motion is simulated here.
    """
    # TODO: in the future, maybe account for effects of wind while on the rail

    # unpack rail variables
    rail_unit_vector_x = launchpad.rail_unit_vector_x
    rail_unit_vector_y = launchpad.rail_unit_vector_y
    rail_unit_vector_z = launchpad.rail_unit_vector_z

    effective_rail_length = launchpad.rail_length - rocket.h_second_rail_button
    effective_rail_height = effective_rail_length * rail_unit_vector_z

    # unpack environmental variables
    launchpad_temp = environment.launchpad_temp

    T_lapse_rate = environment.local_T_lapse_rate
    F_gravity = environment.local_gravity

    multiplier = environment.density_multiplier
    exponent = environment.density_exponent

    # unpack rocket variables
    dry_mass = rocket.dry_mass
    fuel_mass_lookup = rocket.motor.fuel_mass_curve
    engine_thrust_lookup = rocket.motor.thrust_curve
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # initialize simulation variables
    time = t_liftoff # TODO: add half a timestep? In general, go through start and end steps at each flight phase function
    x = 0
    y = 0
    z = 0
    v_x = 0
    v_y = 0
    v_z = 0
    airspeed = 0

    # calculate how much gravity is acting on the rocket along the rail
    F_gravity_rail = F_gravity * rail_unit_vector_z

    # simulate flight from liftoff until the launch rail is cleared
    simulated_values = []

    while z < effective_rail_height:
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
        a_rail = (thrust - F_drag) / mass - F_gravity_rail

        a_x = a_rail * rail_unit_vector_x
        a_y = a_rail * rail_unit_vector_y
        a_z = a_rail * rail_unit_vector_z

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        airspeed = groundspeed # take out if not simulating effects of wind while on rail

        x += v_x * timestep
        y += v_y * timestep
        z += v_z * timestep

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

    # interpolate to find the exact state at rail clearance
    last_state = simulated_values[-1]
    second_last_state = simulated_values[-2]

    # linear interpolation between the last two states
    fraction = (effective_rail_height - second_last_state[3]) / (last_state[3] - second_last_state[3])

    interpolated_state = tuple(
        second_last_state[i] + fraction * (last_state[i] - second_last_state[i])
        for i in range(len(last_state))
    )

    # replace the last state with the interpolated state
    simulated_values[-1] = interpolated_state

    # raise a warning if the rocket doesn't clear the rail before burnout
    if time >= rocket.motor.burn_time:
        print("Warning: Rocket did not clear the rail before burnout.")

    return simulated_values