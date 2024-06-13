# Define Motor, Rocket, LaunchConditions, and Airbrakes classes

import numpy as np

from . import constants as con
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
    
    def __init__(
            self, 
            dry_mass: float, 
            thrust_curve: dict, 
            fuel_mass_curve: dict=None, 
            fuel_mass: float=None
            ):
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

""" TODO Adding wind to the simulation

For first implementation:
- wind will only act in directions parallel to the ground
- wind will have a constant speed and direction for the entire flight
- wind will only affect the rocket's relative airspeed
    - lateral forces will not be considered
- wind will not affect flight from ignition to launch rail clearance
- at launch rail clearance, the rocket will instantly have the wind's velocity added to its velocity vector (instantly weathercock the rocket, keeping the 0 angle of attack assumption used in the simulator)


In the simulation, need to add the wind speed to the rocket's velocity vector and have that relative airspeed vector used to determine the drag force and the rocket's angle of attack (but not the rocket's displacement, which should still be calculated using the rocket's velocity vector).

Use this to get data for Spaceport America for the example configuration: https://www.dropbox.com/sh/swi7jrl14evqmap/AADW6GMVIv87KkOBY1-flsoIa?e=1
    Note that time is in UTC 
    Also use it to add to the Prometheus launch conditions in the airbrakes repo
    Remember that launches can't happen if wind > 20mph, so don't consider data with wind speeds above that when trying to find an average

Is it worth describing the wind as None when not specified and having the simulator run faster by not having to add the wind speed to the velocity vector if it's None? 

Could be added later:    
Varying wind speed and direction with altitude or time, gusts, etc
    - varying_wind_speed: list of tuples
        - Each tuple contains the time (s after ignition) and the wind speed (m/s) at that time. Wind speed is relative to the ground.
    - varying_wind_direction: list of tuples
        - Each tuple contains the time (s after ignition) and the direction of the wind (deg). 0 is a headwind, 90 is a crosswind from the right, 180 is a tailwind, 270 is a crosswind from the left.
    - wind_gusts: list of tuples
        - Each tuple contains the time (s after ignition) and the wind speed (m/s) at that time. Wind speed is relative to the ground.
"""

class LaunchConditions:
    """The LaunchConditions class is used to store the properties of the launch conditions. 

    Attributes
    ----------
    launchpad_pressure : float
        Pressure at the launchpad (Pa).
    launchpad_temp : float
        Temperature at the launchpad (°C).
    L_launch_rail : float
        Length of the launch rail (m).
    launch_angle : float
        Launch angle from horizontal (deg).
    local_gravity : float
        Acceleration due to gravity at the launch site (m/s^2).
    local_T_lapse_rate : float
        Temperature lapse rate at the launch site (°C/m, K/m).
    mean_wind_speed : float
        Mean wind speed relative to the ground (m/s).
    wind_direction : float
        Direction of the (mean) wind relative to the launch direction (deg). 0 is a headwind, 90 is a crosswind from the right, 180 is a tailwind, 270 is a crosswind from the left.
    """

    def __init__(
        self, 
        launchpad_pressure: float,
        launchpad_temp: float,
        L_launch_rail: float,
        launch_angle: float = 90,
        local_gravity: float = None,
        local_T_lapse_rate: float = con.T_lapse_rate,
        latitude: float = None,
        altitude: float = 0,
        # better way to do wind, take a launch direction and a wind direction and calculate the angle between them, then could use the sim for looking at flightpath moving in 3D/relative to the launchpad, but still use the same computational power as just a relative wind direction
        mean_wind_speed = None,
        wind_direction = 0,
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
        launch_angle : float, optional
            Launch angle from horizontal (deg). Defaults to 90 (vertical launch).
        local_gravity : float, optional
            Acceleration due to gravity at the launch site (m/s^2). Defaults to 9.80665.
        local_T_lapse_rate : float, optional
            Temperature lapse rate at the launch site (°C/m, K/m). Defaults to -0.0065.
        latitude : float, optional
            Latitude of the launch site (deg). Used along with altitude to calculate local gravity if local_gravity is not provided. If neither local_gravity nor latitude are provided, local gravity defaults to 9.80665. Defaults to None.
        altitude : float, optional
            Altitude of the launch site (m ASL). Used along with latitude to calculate local gravity if local_gravity is not provided. Defaults to 0.
        mean_wind_speed : float, optional
            Mean wind speed relative to the ground (m/s). Defaults to None.
        wind_direction : float, optional
            Direction of the (mean) wind relative to the launch direction (deg). 0 is a headwind, 90 is a crosswind from the right, 180 is a tailwind, 270 is a crosswind from the left. Defaults to 0 (headwind).
        """
        self.launchpad_pressure = launchpad_pressure
        self.launchpad_temp = launchpad_temp + 273.15
        self.L_launch_rail = L_launch_rail
        self.launch_angle = launch_angle

        self.local_T_lapse_rate = local_T_lapse_rate
        
        if local_gravity:
            self.local_gravity = local_gravity
        elif latitude:
            self.local_gravity = hfunc.get_local_gravity(latitude, altitude)
        else:
            self.local_gravity = con.F_gravity
        
        self.mean_wind_speed = mean_wind_speed
        self.wind_direction = wind_direction        

class Airbrakes:
    """
    The Airbrakes class is used to store the properties of the airbrakes.

    Attributes
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
        self.Cd_brakes = Cd_brakes
        self.max_deployment_rate = max_deployment_rate
        self.max_deployment_angle = max_deployment_angle
        if max_retraction_rate:
            self.max_retraction_rate = max_retraction_rate
        else:
            self.max_retraction_rate = max_deployment_rate

class StateVector:
    """
    The StateVector class is used to store the state of the rocket at a given time. The state is stored as a dictionary with the following keys:

    - t: time (s)
    # do this after adding wind, before breaking stages of flight simulator into separate functions
    """
    
    

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