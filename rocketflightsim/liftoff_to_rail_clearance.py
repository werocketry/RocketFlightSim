import numpy as np

from . import helper_functions as hfunc
from . import constants as con

def flight_sim_liftoff_to_rail_clearance(rocket, launch_conditions, t_liftoff, timestep = con.default_timestep):
    """
    Simulate the flight of a rocket on a launch rail from the time of liftoff unitl the moment the rocket clears the rail.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    launch_conditions : LaunchConditions
        An instance of the LaunchConditions class.
    t_liftoff : float, optional
        Time after ignition at which the rocket lifts off in seconds.
    timestep : float
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        aaa

    Notes
    -----
    This could be done in 1 dimension to save computation time, given the change in air properties over the length of the rail is negligible. Further, if the distance along the rail was taken as height - which it effectively is given most launch angles are close to vertical - accounting for the change in air properties that way would mean an even more negligeable difference compared to the real properties. The 1D motion could then be converted to 3D motion after the rocket has cleared the rail, given the location at the rail exit is determined by the (effective) length of the rail and the direction it is pointed in. For the sake of consistency, 3D motion is simulated here.
    """
    # TODO: in the future, maybe account for effects of wind while on the rail
    # TODO: raise a warning if the rocket doesn't clear the rail before burnout?
    # TODO maybe after first implementation, have it determine the exact state (between timesteps) at rail clearance and replace the last state with that

    # unpack rail variables
    sin_rail_angle_to_vertical = launch_conditions.sin_rail_angle_to_vertical
    cos_rail_angle_to_vertical = launch_conditions.cos_rail_angle_to_vertical

    sin_launch_rail_direction = launch_conditions.sin_launch_rail_direction
    cos_launch_rail_direction = launch_conditions.cos_launch_rail_direction

    effective_L_launch_rail = launch_conditions.L_launch_rail - rocket.h_second_rail_button
    effective_h_launch_rail = effective_L_launch_rail * cos_rail_angle_to_vertical

    # unpack environmental variables
    launchpad_temp = launch_conditions.launchpad_temp

    T_lapse_rate = launch_conditions.local_T_lapse_rate
    F_gravity = launch_conditions.local_gravity

    multiplier = launch_conditions.density_multiplier
    exponent = launch_conditions.density_exponent

    # unpack rocket variables
    dry_mass = rocket.dry_mass
    fuel_mass_lookup = rocket.motor.fuel_mass_curve
    engine_thrust_lookup = rocket.motor.thrust_curve
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # initialize simulation variables
    time = t_liftoff
    # x = 0
    # y = 0
    z = 0
    v_x = 0
    v_y = 0
    v_z = 0
    airspeed = 0

    # simulate flight from liftoff until the launch rail is cleared
    simulated_values = []

    while z < effective_h_launch_rail:
        # update air properties based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # calculate mach number, drag coefficient, and forces
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        F_drag = q * Cd_A_rocket

        # update rocket's motion parameters
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
        airspeed = groundspeed # take out if not simulating effects of wind while on rail

        # add x and y after finishing implementation and comparing speed to old version
        z += v_z * timestep

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