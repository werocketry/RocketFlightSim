import numpy as np

from . import helper_functions as hfunc
from . import constants as con

# TODO: add option for hold-down clamps to dictate liftoff_thrust  
    # have constant stored in launch conditions class?
# TODO: add static friction on the rail? kinetic to next function?
    # for μ ~ 0.7, F_N = m * g * sin(θ_to_vertical) ~ m * 0.8, F_fric ~ m/2 ~ 10 N for Prometheus/Hyperion, very minor. Change in takeoff time would be in the tens of milliseconds at most?
# TODO: account for when keys of engine_thrust_lookup and fuel_mass_lookup aren't aligned

def sim_ignition_to_liftoff(rocket, environment, launchpad):
    """
    Determine the time after ignition at which a rocket lifts off.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    launchpad : Launchpad
        An instance of the Launchpad class.

    Returns
    -------
    float
        Time after ignition at which the rocket lifts off in seconds.

    Notes
    ----- 
    This implementation assumes linear interpolation of mass and thrust curves. This is reasonable given that the curves should have enough points to be relatively smooth.
    """

    # unpack rocket, environment, and launchpad variables
    dry_mass = rocket.dry_mass
    fuel_mass_lookup = rocket.motor.fuel_mass_curve
    engine_thrust_lookup = rocket.motor.thrust_curve
    motor_burn_time = rocket.motor.burn_time
    liftoff_thrust_to_mass_ratio = environment.local_gravity * launchpad.rail_unit_vector_z

    hold_down_clamp_force = launchpad.hold_down_clamp_force
    hold_down_clamp_release_time = launchpad.hold_down_clamp_release_time

    # calculate needed thrusts at each key in fuel_mass_lookup before burnout
    masses = [hfunc.mass_at_time(time, dry_mass, fuel_mass_lookup) for time in fuel_mass_lookup.keys() if time < motor_burn_time]
    masses.append(dry_mass)

    liftoff_thrusts = {key: mass * liftoff_thrust_to_mass_ratio for key, mass in zip(fuel_mass_lookup.keys(), masses)}

    # apply hold-down clamps if necessary
    if hold_down_clamp_force or hold_down_clamp_release_time:
        # if hold-down clamps release at a certain time
        if hold_down_clamp_release_time:
            # add interpolated thrust at release time to engine_thrust_lookup and liftoff_thrusts dicts
            if hold_down_clamp_release_time not in engine_thrust_lookup.keys():
                engine_thrust_lookup[hold_down_clamp_release_time] = np.interp(hold_down_clamp_release_time, list(engine_thrust_lookup.keys()), list(engine_thrust_lookup.values()))
                liftoff_thrusts[hold_down_clamp_release_time] = np.interp(hold_down_clamp_release_time, list(liftoff_thrusts.keys()), list(liftoff_thrusts.values()))

                # order the dictionaries by key
                engine_thrust_lookup = dict(sorted(engine_thrust_lookup.items()))
                liftoff_thrusts = dict(sorted(liftoff_thrusts.items()))

            # if hold-down clamps release at a certain time but have no specified force limit, the rocket may only lift off at or after release time
            if not hold_down_clamp_force:
                # raise exception if hold-down clamps release the rocket after the motor burns out
                if hold_down_clamp_release_time > motor_burn_time:
                    raise Exception("The hold-down clamps hold the rocket down for longer than the motor burns")

                # if thrust > liftoff thrust at release time, moment of release is the time of liftoff
                if engine_thrust_lookup[hold_down_clamp_release_time] > liftoff_thrusts[hold_down_clamp_release_time]:
                    return hold_down_clamp_release_time

                # if rocket doesn't lift off at moment of release, remove liftoff thrusts before release time
                liftoff_thrusts = {key: thrust for key, thrust in liftoff_thrusts.items() if key >= hold_down_clamp_release_time}
                engine_thrust_lookup = {key: thrust for key, thrust in engine_thrust_lookup.items() if key >= hold_down_clamp_release_time}

            # if hold-down clamps release at a certain time and have a specified force limit, the rocket may lift off before release time
            else:
                # add hold-down clamp force to liftoff thrusts before release time
                liftoff_thrusts = {
                    key: (thrust + hold_down_clamp_force if key < hold_down_clamp_release_time else thrust)
                    for key, thrust in liftoff_thrusts.items()
                }

        # if hold-down clamps only release when a certain force is reached
        else:
                # add hold-down clamp force to liftoff thrusts
                liftoff_thrusts_clamped = {key: thrust + hold_down_clamp_force for key, thrust in liftoff_thrusts.items()}
                # if hold-down clamps don't release at a certain time, always use the clamped thrusts
                liftoff_thrusts = liftoff_thrusts_clamped


    # find the first time when thrust exceeds liftoff thrust, or raise an exception if the rocket never lifts off
    try:
        post_liftoff_key = next(key for key, thrust in engine_thrust_lookup.items() if thrust > liftoff_thrusts[key])
    except StopIteration:
        raise Exception("The motor never produces enough thrust for the rocket to lift off")

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