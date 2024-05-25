# Define Motor, Rocket, LaunchConditions, and Airbrakes classes

import numpy as np
from . import helper_functions as hfunc

class Motor:
    """
    The Motor class is used to store the properties of a rocket motor. The properties are:

    - dry_mass: mass of the motor without fuel (kg)
    - thrust_curve: dictionary of thrust (N) at time (s after ignition)
    - total_impulse: total impulse of the motor (Ns)
    - burn_time: time it takes for the motor to burn all of its fuel (s)
    - fuel_mass_curve: dictionary of mass (kg) at time (s after ignition)
    - fuel_mass: total mass of fuel in the motor before ignition (kg)

    If fuel_mass_curve is not provided but feul_mass is, fuel_mass_curve is calculated from the thrust_curve and fuel_mass (assuming fuel burn is proportional to thrust). If fuel_mass_curve is provided, fuel_mass is set to the initial mass in fuel_mass_curve. If neither are provided, fuel_mass and fuel_mass_curve are set to 0.
    """
    # TODO: take eng files as inputs
    def __init__(self, dry_mass, thrust_curve, fuel_mass_curve=None, fuel_mass=None):
        self.dry_mass = dry_mass
        self.thrust_curve = thrust_curve

        self.total_impulse = np.trapz(list(thrust_curve.values()), list(thrust_curve.keys()))
        self.burn_time = max(thrust_curve.keys())
        
        if fuel_mass_curve:
            self.fuel_mass_curve = fuel_mass_curve
            self.fuel_mass = fuel_mass_curve[0]
        elif fuel_mass:
            self.fuel_mass = fuel_mass
            self.fuel_mass_curve = {0: fuel_mass}
            times = list(self.thrust_curve.keys())
            for t in range(1, len(times)):
                self.fuel_mass_curve[times[t]] = self.fuel_mass_curve[times[t-1]] - (thrust_curve[times[t]] + thrust_curve[times[t-1]])/2 * (times[t] - times[t-1]) / self.total_impulse * fuel_mass
        else:
            self.fuel_mass = 0
            self.fuel_mass_curve = {
                0: 0,
                self.burn_time: 0
                }


class Rocket:
    """
    The Rocket class is used to store the properties of a rocket. The properties are:

    - rocket_mass: dry mass of the rocket without the motor (kg)
    - motor: Motor object
    - A_rocket: cross-sectional area of the rocket (m^2). Must be the same used when the Cd_rocket_at_Ma was calculated.
    - Cd_rocket_at_Ma: coefficient of drag of the rocket as a function of Mach number. Defaults to a constant 0.45, which is in the ballpark of what most comp rockets our size have.
    - h_second_rail_button: height of the second rail button from the bottom of the rocket (m). This is the upper button if there's only 2. Defaults to 0.69m, which is what Prometheus had. Doesn't matter much if it's not set as it changes apogee by less than 10ft when it's at 0.

    - dry_mass: total mass of the rocket without fuel (kg)
    - Cd_A_rocket: coefficient of drag of the rocket multiplied by the cross-sectional area of the rocket (m^2)
    """

    def __init__(
        self,
        rocket_mass,
        motor,
        A_rocket,
        Cd_rocket_at_Ma = 0.45,
        h_second_rail_button=0.69,
    ):
        self.rocket_mass = rocket_mass
        self.motor = motor
        self.A_rocket = A_rocket
        self.Cd_rocket_at_Ma = Cd_rocket_at_Ma
        self.h_second_rail_button = h_second_rail_button

        self.dry_mass = rocket_mass + motor.dry_mass
        
        if callable(Cd_rocket_at_Ma):
            def Cd_A_rocket_fn(Ma):
                return Cd_rocket_at_Ma(Ma) * A_rocket
        else:
            def Cd_A_rocket_fn(Ma): return Cd_rocket_at_Ma * A_rocket
            # TODO: make it actually operate as a constant if it's not a function
        self.Cd_A_rocket = Cd_A_rocket_fn


class LaunchConditions:
    """
    The LaunchConditions class is used to store the properties of the launch conditions. The properties are:

    - launchpad_pressure: pressure at the launchpad (Pa)
    - launchpad_temp: temperature at the launchpad (°C)
    - L_launch_rail: length of the launch rail (m)
    - launch_angle: launch angle from horizontal (deg). SAC comp rules say minimum of 6 deg off of vertical, but they pick it based on wind and pad location, so completely out of our control, and we just know it's between 6 and 15 deg
    - local_gravity: acceleration due to gravity at the launch site (m/s^2). Defaults to 9.80665
    - local_T_lapse_rate: temperature lapse rate at the launch site (°C/m, K/m). Defaults to -0.0065
    - latitude: latitude of the launch site (deg). Used to calculate local gravity if local_gravity is not provided. If neither are provided, local gravity defaults to 9.807
    - altitude: altitude of the launch site (m ASL). Defaults to 0
    """

    def __init__(self, launchpad_pressure, launchpad_temp, L_launch_rail, launch_angle, local_gravity=None, local_T_lapse_rate=None, latitude=None, altitude=0):
        self.launchpad_pressure = launchpad_pressure
        self.launchpad_temp = launchpad_temp # TODO: maybe make it convert to Kelvin here
        self.L_launch_rail = L_launch_rail
        self.launch_angle = launch_angle

        self.local_T_lapse_rate = local_T_lapse_rate
        
        if local_gravity:
            self.local_gravity = local_gravity
        elif latitude:
            self.local_gravity = hfunc.get_local_gravity(latitude, altitude)
        else:
            self.local_gravity = None
        

class Airbrakes:
    """
    The Airbrakes class is used to store the properties of the airbrakes. The properties are:

    - num_flaps: number of airbrakes flaps
    - A_flap: cross-sectional area of each flap (m^2)
    - Cd_brakes: coefficient of drag of the airbrakes
    - max_deployment_speed: maximum speed at which the airbrakes can be deployed (deg/s)
    - max_deployment_angle: maximum angle that the flaps can deploy to (deg)
    """

    def __init__(
        self, num_flaps, A_flap, Cd_brakes, max_deployment_speed, max_deployment_angle
    ):
        self.num_flaps = num_flaps
        self.A_flap = A_flap
        self.Cd_brakes = Cd_brakes
        self.max_deployment_speed = max_deployment_speed
        self.max_deployment_angle = max_deployment_angle


class PastFlight ():
    """
    Stores the rocket, launch conditions, and apogee of a past flight
    likely add more things like max speed, max acceleration later
    """
    
    def __init__(self, rocket, launch_conditions, apogee, name = None):
        self.rocket = rocket
        self.launch_conditions = launch_conditions
        self.apogee = apogee
        self.name = name