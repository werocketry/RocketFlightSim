import numpy as np
from .. import constants as con
from .. import helper_functions as hfunc
from ..classes.rocket import Rocket
from ..classes.environment import Environment


def max_theoretical_accel_motor(rocket: Rocket, environment: Environment=None):
    """
    Returns the maximum theoretical acceleration that a rocket can experience during motor burn. Assumes no drag, the motor performs at or below spec max thrust, and no parts of the rocket fall off.

    Args
    ----
    - rocket (Rocket): A Rocket object.
    - environment (Environment, optional): An Environment object.

    Returns
    -------
    - float: The maximum theoretical acceleration the rocket can experience in m/s^2.
    """
    if environment:
        F_gravity = environment.local_gravity
    else:
        F_gravity = con.F_gravity

    max_thrust = max(rocket.motor.thrust_curve.values())
    time_of_max_thrust = max(rocket.motor.thrust_curve, key=rocket.motor.thrust_curve.get)
    mass_at_max_thrust = hfunc.mass_at_time(time_of_max_thrust, rocket.dry_mass, rocket.motor.fuel_mass_curve)

    max_acceleration = max_thrust / mass_at_max_thrust - F_gravity

    return max_acceleration

def max_theoretical_speed(rocket: Rocket, environment: Environment=None, timestep: float=0.0005):
    """
    Returns the maximum theoretical theoretical speed that a rocket can reach. Assumes no drag, the motor performs at or below spec thrust curve, and no parts of the rocket fall off.

    Args
    ----
    - rocket (Rocket): A Rocket object.
    - environment (Environment, optional): An Environment object.
    - timestep (float, optional): The time increment for the integration in seconds.

    Returns
    -------
    - float: The maximum theoretical speed the rocket can reach in m/s.
    """
    t = 0
    v = 0
    v_max = 0
    if environment:
        F_gravity = environment.local_gravity
    else:
        F_gravity = con.F_gravity
    
    while t < rocket.motor.burn_time:
        mass = hfunc.mass_at_time(t, rocket.dry_mass, rocket.motor.fuel_mass_curve)
        thrust = hfunc.thrust_at_time(t, rocket.motor.thrust_curve)
        acceleration = thrust / mass - F_gravity
        if acceleration < 0:
            acceleration = 0
        v += acceleration * timestep
        if v > v_max:
            v_max = v
        t += timestep
    
    return v_max

# TODO: add max_theoretical_altitude? maybe just call on the flight function and use no drag. But would a dedicated one using max_theoretical_speed be significantly faster?