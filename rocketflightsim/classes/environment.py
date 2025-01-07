import numpy as np
from .. import constants as con
from .. import helper_functions as hfunc

class Environment:
    """
    The Environment class is used to store the properties of the environment that a rocket is flying through.

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

    mean_wind_speed : float
        Mean wind speed relative to the ground (m/s).
    wind_heading : float
        Direction the wind is headed towards (rad). 0 is north, π/2 is east, π is south, 3π/2 is west.
    """
    # TODO: maybe incorporate air humidity
    # TODO: would it make sense to make the air density function a method of this class?
    # TODO: more advanced atmospheric model (particularly non-static lapse rate, also look at varying gravity again, would be cool to sim something like a Saturn V) for rockets flying beyond the troposphere. Or could just redefine the environment at certain altitudes
    def __init__(
        self, 
        launchpad_pressure : float,
        launchpad_temp : float,
        local_gravity : float = None,
        local_T_lapse_rate : float = con.T_lapse_rate,
        latitude : float = None,
        altitude : float = 0,
        mean_wind_speed : float = 0,
        wind_heading : float = 0,
    ):
        """Initialize an Environment object. 
        
        Parameters
        ----------
        launchpad_pressure : float
            Pressure at the launchpad (Pa).
        launchpad_temp : float
            Temperature at the launchpad (°C).

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
            Direction the wind is headed towards (deg). 0 is north, 90 is east, 180 is south, 270 is west. Defaults to 0.
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

        self.mean_wind_speed = mean_wind_speed
        self.wind_heading = np.deg2rad(wind_heading)



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
    - more complex wind model:
        - https://en.wikipedia.org/wiki/Wind_profile_power_law
        - https://en.wikipedia.org/wiki/Log_wind_profile

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
