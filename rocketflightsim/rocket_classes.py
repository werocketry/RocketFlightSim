# Define classes used by the package

import numpy as np

from . import constants as con
from . import helper_functions as hfunc

class Motor:
    """
    The Motor class is used to store the properties of a rocket motor. The properties are:

    - dry_mass: mass of the motor without fuel (kg)
    - thrust_curve: dictionary of thrust (N) produced by the motor at time after ignition (s)
    - total_impulse: total impulse of the motor (Ns)
    - burn_time: time it takes for the motor to burn all of its fuel (s)
    - fuel_mass_curve: dictionary of fuel mass (kg) at time after ignition (s)
    - fuel_mass: total mass of fuel in the motor before ignition (kg)

    If fuel_mass_curve is not provided but fuel_mass is, fuel_mass_curve is calculated from the thrust_curve and fuel_mass (assuming fuel burn is proportional to thrust). If fuel_mass_curve is provided, fuel_mass is set to the initial mass in fuel_mass_curve. If neither are provided, fuel_mass and fuel_mass_curve are set to 0.
    """

    def __init__(
            self, 
            dry_mass: float, 
            thrust_curve: dict, 
            fuel_mass_curve: dict=None, 
            fuel_mass: float=None
            ):
        """Initializes the Motor object.

        Attributes
        ----------
        dry_mass : float
            Mass of the motor without fuel (kg).
        thrust_curve : dict
            Dictionary of thrust (N) produced by the motor at time after ignition (s).
        total_impulse : float
            Total impulse of the motor (Ns).
        burn_time : float
            Time it takes for the motor to burn all of its fuel (s).
        fuel_mass_curve : dict
            Dictionary of fuel mass (kg) at time after ignition (s).
        fuel_mass : float
            Total mass of fuel in the motor before ignition (kg). # add explanatinos of use/take awahy what's not used in init
        """
        self.dry_mass = dry_mass
        self.thrust_curve = thrust_curve

        self.total_impulse = np.trapz(list(thrust_curve.values()), list(thrust_curve.keys())) # TODO: not important for this in and of itself, but for future additions, look at difference between using numpy.trapz and scipy.integrate.trapz or even other integration functions
        # TODO: maybe add a test for the simulator function to see if total impulse was added to the rocket's dry mass in the first instant after ignition, it would give a higher max acceleration than the simulator predicts
        self.burn_time = max(thrust_curve.keys())
        # TODO: add burn efficiency, some propelant mass (~2-5% ?) becomes dry mass (can just assign it to dry mass at the start of the sim/at class init)
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
    The Rocket class is used to store the properties of a rocket.

    Attributes
    ----------
    rocket_mass : float
        Dry mass of the rocket without the motor (kg).
    motor : Motor object
        The rocket's motor.
    A_rocket : float
        Cross-sectional area of the rocket (m^2) used when Cd_rocket_at_Ma was calculated.
    Cd_rocket_at_Ma : float or function
        Coefficient of drag of the rocket. May be given as a function of Mach number or as a constant.
    h_second_rail_button : float
        Height of the second rail button from the bottom of the rocket (m). This is the upper button if there are only 2.
    dry_mass : float
        Total mass of the rocket without fuel (kg).
    Cd_A_rocket : function
        Coefficient of drag of the rocket multiplied by the cross-sectional area of the rocket (m^2).
    """

    def __init__(
        self,
        rocket_mass : float,
        motor : Motor,
        A_rocket : float,
        Cd_rocket_at_Ma = 0.45,
        h_second_rail_button : float = 0.69,
    ):
        """Initializes the Rocket object.

        Parameters
        ----------
        rocket_mass : float
            Dry mass of the rocket without the motor (kg).
        motor : Motor object
            The rocket's motor.
        A_rocket : float
            Cross-sectional area of the rocket (m^2). Must be the same used when the Cd_rocket_at_Ma was calculated.
        Cd_rocket_at_Ma : float or function, optional
            Coefficient of drag of the rocket. May be given as a function of Mach number or as a constant. Defaults to a constant 0.45, which is in the ballpark of what most student team competition rockets our size have.
        h_second_rail_button : float, optional
            Height of the second rail button from the bottom of the rocket (m). This is the upper button if there are only 2. Defaults to 0.7m, which is reasonable for most student team competition rockets. Doesn't matter much if it's not set as it changes apogee by less than 10ft on a 10k ft launch when set to 0.
        """

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

""" TODO Improve wind in the simulation

First (current) implementation:
- wind only acts in directions parallel to the ground
- wind has constant speed and direction for the entire flight
- wind only affects a rocket's airspeed, affecting drag and angle of attack
    - lateral forces not considered
- wind has no effect on flight from ignition to launch rail clearance
- at rail clearance, a rocket instantly has 20% of the wind's velocity added to its velocity vector to get the new airspeed, then the full vector added at burnout. Placeholder for a better mode of transition from the angle of attack leaving the launch rail to a 0 deg AoA

Next up:
    - Use this to get data for Spaceport America for the example configuration: https://www.dropbox.com/sh/swi7jrl14evqmap/AADW6GMVIv87KkOBY1-flsoIa?e=1
        - Note that time is in UTC 
        - Also use it to add to the Prometheus launch conditions in the airbrakes repo
        - Remember that launches can't happen if wind > 20mph, so don't consider data with wind speeds above that when trying to find an average
    - incorporate looking at/recording/visualizing flightpath moving in 3D/relative to the launchpad
    - make AoA a real variable/truly incorporate it into the sim

Could be added later:
    - possibly set windspeed as None when not specified and have the simulator run faster by not having to deal with wind. Likely after the break up of the simulation function into different functions for different phases of flight. Maybe a series of sim functions will be chosen from?
    - Varying wind speed and direction with altitude or time, gusts, etc
        - varying_wind_speed: list of tuples
            - Each tuple contains the time (s after ignition) and the wind speed (m/s) at that time. Wind speed is relative to the ground.
        - varying_wind_heading: list of tuples
            - Each tuple contains the time (s after ignition) and the direction of the wind (deg). 0 is a headwind, 90 is a crosswind from the right, 180 is a tailwind, 270 is a crosswind from the left.
        - wind_gusts: list of tuples
            - Each tuple contains the time (s after ignition) and the wind speed (m/s) at that time. Wind speed is relative to the ground.
        - vertical wind/updrafts/downdrafts
"""

class LaunchConditions:
    """The LaunchConditions class is used to store the properties of the launch conditions. 

    Attributes
    ----------
    launchpad_pressure : float
        Pressure at the launchpad (Pa).
    launchpad_temp : float
        Temperature at the launchpad (K).
    launchpad_air_density : float
        Air density at the launchpad (kg/m^3).

    local_gravity : float
        Acceleration due to gravity at the launch site (m/s^2).
    local_T_lapse_rate : float
        Temperature lapse rate at the launch site (°C/m, K/m).
    density_multiplier : float
        A constant derived from the temperature and pressure at the launchpad, the lapse rate, the specific gas constant for air, and the magnitude of the force of gravity. Used in the air_density_optimized function. Equal to P_launchpad / (R_air * pow(T_launchpad, - F_gravity / (R_air * T_lapse_rate))).
    density_exponent : float
        A constant derived from the lapse rate, the specific gas constant for air, and the magnitude of the force of gravity. Used in the air_density_optimized function. Equal to - F_gravity / (R_air * T_lapse_rate) - 1.

    L_launch_rail : float
        Length of the launch rail (m).
    angle_to_vertical : float
        Angle of the rocket to the vertical when it's on the pad (rad).
    sin_rail_angle_to_vertical : float
        Sine of the angle of the launch rail from the vertical.
    cos_rail_angle_to_vertical : float
        Cosine of the angle of the launch rail from the vertical.
    launch_rail_direction : float
        Direction of the launch rail (rad). 0 is north, π/2 is east, π is south, 3π/2 is west.
    sin_launch_rail_direction : float
        Sine of the direction of the launch rail.
    cos_launch_rail_direction : float
        Cosine of the direction of the launch rail.

    mean_wind_speed : float
        Mean wind speed relative to the ground (m/s).
    wind_heading : float
        Direction the (mean) wind is headed towards (rad). 0 is north, π/2 is east, π is south, 3π/2 is west.
    """
    # TODO: have it calculate the atmospheric conditions on the ground in init
    # TODO: maybe incorporate air humidity?
    # TODO: move rail trig calculations here
    # TODO: move launch rail attributes to a separate class, maybe contained inside this one? More for organization than anything else. Maybe rename this one LaunchEnvironment or something similar
    # TODO: would it make sense to make the air density function a method of this class?
    def __init__(
        self, 
        launchpad_pressure: float,
        launchpad_temp: float,
        L_launch_rail: float,
        launch_rail_elevation: float = 90,
        launch_rail_direction: float = 0,
        local_gravity: float = None,
        local_T_lapse_rate: float = con.T_lapse_rate,
        latitude: float = None,
        altitude: float = 0,
        mean_wind_speed = 0,
        wind_heading = 0,
    ):
        """Initializes the LaunchConditions object. 
        
        Parameters
        ----------
        launchpad_pressure : float
            Pressure at the launchpad (Pa).
        launchpad_temp : float
            Temperature at the launchpad (°C).
        L_launch_rail : float
            Length of the launch rail (m).
        launch_rail_elevation : float
            Angle of the launch rail from horizontal (deg). Defaults to 90 (vertical launch rail).
        launch_rail_direction : float
            Direction of the launch rail (deg). 0 is north, 90 is east, 180 is south, 270 is west. Defaults to 0 (north).
        local_gravity : float, optional
            Acceleration due to gravity at the launch site (m/s^2). Defaults to 9.80665.
        local_T_lapse_rate : float, optional
            Temperature lapse rate at the launch site (°C/m, K/m). Defaults to -0.0065.
        latitude : float, optional
            Latitude of the launch site (deg). Used along with altitude to calculate local gravity if local_gravity is not provided. If neither local_gravity nor latitude are provided, local gravity defaults to 9.80665. Defaults to None.
        altitude : float, optional
            Altitude of the launch site (m ASL). Used along with latitude to calculate local gravity if local_gravity is not provided. Defaults to 0.
        mean_wind_speed : float, optional
            Mean wind speed relative to the ground (m/s). Defaults to 0.
        wind_heading : float, optional
            Direction the (mean) wind is headed towards (deg). 0 is north, 90 is east, 180 is south, 270 is west. Defaults to 0.
        """
        self.launchpad_pressure = launchpad_pressure
        self.launchpad_temp = launchpad_temp + 273.15
        self.launchpad_air_density = hfunc.air_density_fn(launchpad_pressure, self.launchpad_temp)

        self.local_T_lapse_rate = local_T_lapse_rate
        if local_gravity:
            self.local_gravity = local_gravity
        elif latitude:
            self.local_gravity = hfunc.get_local_gravity(latitude, altitude)
        else:
            self.local_gravity = con.F_gravity

        self.density_multiplier = launchpad_pressure / (con.R_specific_air * pow(self.launchpad_temp, - self.local_gravity / (con.R_specific_air * local_T_lapse_rate)))
        self.density_exponent = - self.local_gravity / (con.R_specific_air * local_T_lapse_rate) - 1

        self.L_launch_rail = L_launch_rail
        self.launch_rail_direction = np.deg2rad(launch_rail_direction)
        self.sin_launch_rail_direction = np.sin(self.launch_rail_direction)
        self.cos_launch_rail_direction = np.cos(self.launch_rail_direction)

        if launch_rail_elevation == 90:
            launch_rail_elevation = 89.999999
            # TODO: find a better workaround
                # np.atan2 for compass heading?

        self.angle_to_vertical = np.deg2rad(90 - launch_rail_elevation)
        self.sin_rail_angle_to_vertical = np.sin(self.angle_to_vertical)
        self.cos_rail_angle_to_vertical = np.cos(self.angle_to_vertical)

        self.mean_wind_speed = mean_wind_speed
        self.wind_heading = np.deg2rad(wind_heading)

class Airbrakes:
    """
    The Airbrakes class is used to store the properties of the airbrakes.

    Attributes
    ----------
    num_flaps : int
        Number of airbrake flaps.
    A_flap : float
        Cross-sectional area of each flap (m^2).
    A_brakes : float
        Total cross-sectional area of the airbrakes (m^2).
    Cd_brakes : float
        Coefficient of drag of the airbrakes.
    max_deployment_angle : float
        Maximum angle that the flaps can deploy to (deg).
    max_deployment_rate : float
        Maximum rate at which the airbrakes can be deployed (deg/s).
    max_retraction_rate : float
        Maximum rate at which the airbrakes can be retracted (deg/s).
    """

    def __init__(
        self, 
        num_flaps : int,
        A_flap : float,
        Cd_brakes : float,
        max_deployment_angle : float,
        max_deployment_rate : float,
        max_retraction_rate : float = None,
    ):
        """Initializes the Airbrakes object.

        Parameters
        ----------
        num_flaps : int
            Number of airbrake flaps.
        A_flap : float
            Cross-sectional area of each flap (m^2).
        Cd_brakes : float
            Coefficient of drag of the airbrakes.
        max_deployment_angle : float
            Maximum angle that the flaps can deploy to (deg).
        max_deployment_rate : float
            Maximum rate at which the airbrakes can be deployed (deg/s).
        max_retraction_rate : float, optional
            Maximum rate at which the airbrakes can be retracted (deg/s). Defaults to max_deployment_rate.
        """
        self.num_flaps = num_flaps
        self.A_flap = A_flap
        self.A_brakes = A_flap * num_flaps

        self.Cd_brakes = Cd_brakes

        self.max_deployment_rate = max_deployment_rate
        self.max_deployment_angle = max_deployment_angle
        if max_retraction_rate:
            self.max_retraction_rate = max_retraction_rate
        else:
            self.max_retraction_rate = max_deployment_rate

class StateVector:
    """ Needed? Just pass needed inputs into the flight function for the phase in the function that combines all the phases?
    
    The StateVector class is used to store the state of a rocket's flight at a given time. The state is stored as a dictionary with the following keys:

    - launch_conditions: The LaunchConditions object associated with the flight.
    - t: time (s)
    - x: displacement east (m) - add after finishing implementation and comparing speed to old version
    - y: displacement north (m)- add after finishing implementation and comparing speed to old version
    - z: altitude (m)
    - v_x
    - v_y
    - v_z
    - groundspeed
    - airspeed
    - a_x
    - a_y
    - a_z
    - a
    - temp - needed? won't it just be re-calculated if the above are passed to the next flight phase function?
    - air_density - same as temp
    - q - same as temp
    - Ma - same as temp
    - angle_to_vertical
    """
    # compass heading/angle to vertical as methods?
    def __init__(self, ):
        """
        """

class Flightpath:
    """
    The Flightpath class 
    just make it a series of StateVectors? Does it need a class in that case?
    """

class PastFlight ():
    """
    Stores the rocket, launch conditions, and apogee of a past flight
    likely add more things like max speed, max acceleration later. Also the option to feed a full flightpath, good for comparisons of sim projection to actual flightpaths
    """

    def __init__(self, rocket, launch_conditions, apogee = None, name = None):
        self.rocket = rocket
        self.launch_conditions = launch_conditions
        self.apogee = apogee
        self.name = name