import numpy as np

from . import helper_functions as hfunc
from . import constants as con

# TODO: if rocket never produces enough thrust to lift off, raise a custom exception
# TODO: add option for hold-down clamps to dictate liftoff_thrust - have constant stored in launch conditions class, along with liftoff_thrust_to_mass_ratio
# TODO: add static friction on the rail? kinetic to next function?
    # for μ ~ 0.7, F_N = m * g * sin(θ_to_vertical) ~ m * 0.8, F_fric ~ m/2 ~ 10 N for Prometheus/Hyperion, very minor. Change in takeoff time would be in the tens of milliseconds at most?
# TODO: account for when keys of engine_thrust_lookup and fuel_mass_lookup aren't aligned

def flight_sim_ignition_to_liftoff(rocket, launch_conditions):
    """
    Determine the time after ignition at which a rocket lifts off.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    launch_conditions : LaunchConditions
        An instance of the LaunchConditions class.

    Returns
    -------
    float
        Time after ignition at which the rocket lifts off in seconds.

    Notes
    ----- 
    This implementation assumes linear interpolation of mass and thrust curves. This is reasonable given that the curves should have enough points to be relatively smooth.
    """

    liftoff_thrust_to_mass_ratio = launch_conditions.local_gravity * launch_conditions.cos_rail_angle_to_vertical # move to init of launch_conditions class?

    # unpack rocket and launch_conditions
    dry_mass = rocket.dry_mass
    fuel_mass_lookup = rocket.motor.fuel_mass_curve
    engine_thrust_lookup = rocket.motor.thrust_curve

    # calculate needed thrusts at each key in fuel_mass_lookup before burnout
    masses = [hfunc.mass_at_time(time, dry_mass, fuel_mass_lookup) for time in fuel_mass_lookup.keys() if time < rocket.motor.burn_time]
    liftoff_thrusts = {key: mass * liftoff_thrust_to_mass_ratio for key, mass in zip(fuel_mass_lookup.keys(), masses)}

    # find the first time when thrust exceeds lifroff thrust
    post_liftoff_key = next(key for key, thrust in engine_thrust_lookup.items() if thrust > liftoff_thrusts[key])
    # find last key before liftoff
    pre_liftoff_key = max(key for key in engine_thrust_lookup.keys() if key < post_liftoff_key)

    # equation of line for thrust between pre_liftoff_key and post_liftoff_key
    thrust_slope = (engine_thrust_lookup[post_liftoff_key] - engine_thrust_lookup[pre_liftoff_key]) / (post_liftoff_key - pre_liftoff_key)
    thrust_intercept = engine_thrust_lookup[pre_liftoff_key] - thrust_slope * pre_liftoff_key
    # equation of line for liftoff_thrusts between pre_liftoff_key and post_liftoff_key
    liftoff_thrust_slope = (liftoff_thrusts[post_liftoff_key] - liftoff_thrusts[pre_liftoff_key]) / (post_liftoff_key - pre_liftoff_key)
    liftoff_thrust_intercept = liftoff_thrusts[pre_liftoff_key] - liftoff_thrust_slope * pre_liftoff_key

    # interpolate time of liftoff
    time_of_liftoff = (liftoff_thrust_intercept - thrust_intercept) / (thrust_slope - liftoff_thrust_slope)

    return time_of_liftoff