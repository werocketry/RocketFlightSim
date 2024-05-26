import numpy as np
from . import constants as con

# aerodynamics
def temp_at_height(h, launchpad_temp, lapse_rate = con.T_lapse_rate):
    """
    Calculate the temperature at a given height above the launchpad. Within the troposphere, the temperature decreases linearly with height at a rate known as the lapse rate. The lapse rate is typically around 6.5 degrees Celsius per kilometer. 

    Args:
    - h (float): Height above the launchpad in meters.
    - launchpad_temp (float): Temperature at the launchpad in Celsius or Kelvin.
    - lapse_rate (float, optional): Rate at which temperature decreases with height in degrees Celsius or Kelvin per meter. Defaults to the standard lapse rate of 0.0065.

    Returns:
    - float: Temperature at the given height in Celsius or Kelvin (same as input).
    """
    return launchpad_temp + (h * lapse_rate)

def air_density_optimized(temp, multiplier, exponent):
    """
    Calculate the density of air at a given height above the launchpad.

    Args:
    - temp (float): Temperature at the given height in Kelvin.
    - multiplier (float): A constant derived from the temperature and pressure at the launchpad, the lapse rate, the specific gas constant for air, and the magnitude of the force of gravity. Calculated at the start of the simulation script outside of the main loops. Equal to P_launchpad / (R_air * pow(T_launchpad, - F_gravity / (R_air * T_lapse_rate))).
    - exponent (float): A constant derived from the lapse rate, the specific gas constant for air, and the magnitude of the force of gravity. Calculated at the start of the simulation script outside of the main loops. Equal to - F_gravity / (R_air * T_lapse_rate) - 1.

    Returns:
    - float: Air density at the given height in kilograms per cubic meter.
    """
    return multiplier * pow(temp, exponent)

def calculate_dynamic_pressure(air_density, speed):
    """
    Calculate the dynamic pressure imparted on a solid moving through a fluid.

    Args:
    - air_density (float): The density of the fluid.
    - speed (float): The relative speed of the solid and the fluid.

    Returns:
    - float: The dynamic pressure on the solid.
    """
    return 0.5 * air_density * (speed ** 2)

def mach_number_fn(v, temp):
    """
    Calculate the Mach number of an object moving through air at a given temperature.

    Args:
    - v (float): Velocity of the object relative to the air in meters per second.
    - temp (float): Air temperature in Kelvin.

    Returns:
    - float: Mach number (dimensionless).
    """
    return v / np.sqrt(con.adiabatic_index_air_times_R_specific_air * temp)

# gravity
def get_local_gravity(latitude, h = 0, h_expected = None):
    """
    Calculate the acceleration due to gravity at a given latitude and height above sea level.

    Args:
    - latitude (float): Latitude of launch site in degrees.
    - h (float): Ground level elevation above sea level in meters. Defaults to 0.
    - h_expected (float): Expected height the rocket will reach above sea level in meters. Defaults to None, in which case the function will return the acceleration due to gravity at the launchpad instead of the average between the launchpad and the expected apogee.

    Returns:
    - float: Acceleration due to gravity in meters per second squared.

    Based on the International Gravity Formula 1980 (IGF80) model, as outlined in https://en.wikipedia.org/wiki/Theoretical_gravity#International_gravity_formula_1980
    """

    gamma_a = 9.780327  # m/s^2
    c1 = 0.0052790414
    c2 = 0.0000232718
    c3 = 0.0000001262
    c4 = 0.0000000007

    phi = np.deg2rad(latitude)

    gamma_0 = gamma_a * (1 + c1 * np.sin(phi)**2 + c2 * np.sin(phi)**4 + c3 * np.sin(phi)**6 + c4 * np.sin(phi)**8)


    k1 = 3.15704e-07  # 1/m
    k2 = 2.10269e-09  # 1/m
    k3 = 7.37452e-14  # 1/m^2

    g_launchpad = gamma_0 * (1 - (k1 - k2 * np.sin(phi)**2) * h + k3 * h**2)

    if h_expected:
        g_apogee = gamma_0 * (1 - (k1 - k2 * np.sin(phi)**2) * h_expected + k3 * h_expected**2)
        return (g_launchpad + g_apogee) / 2
    else:
        return g_launchpad

# not used in simulator
def pressure_at_height(h, launchpad_temp, launchpad_pressure):
    """
    Calculate the air pressure at a given height above the launchpad.

    Args:
    - h (float): Height above the launchpad in meters.
    - launchpad_temp (float): Temperature at the launchpad in Kelvin.
    - launchpad_pressure (float): Air pressure at the launchpad in Pascals.

    Returns:
    - float: Air pressure at the given height in Pascals.
    """ # note, could use a specific sim's local gravity and lapse rate to be more accurate
    return launchpad_pressure * pow(
        (1 - (h * con.T_lapse_rate / launchpad_temp)),
        (con.F_gravity / (con.R_specific_air * con.T_lapse_rate))
    )

def air_density_fn(pressure, temp):
    """
    Calculate the density of air at a given pressure and temperature.

    Args:
    - pressure (float): Pressure in Pascals.
    - temp (float): Temperature in Kelvin.

    Returns:
    - float: Air density in kilograms per cubic meter.
    """
    return pressure / (con.R_specific_air * temp)

def lookup_dynamic_viscosity(temp):
    """
    Look up the dynamic viscosity of air at a given temperature.

    Args:
    - temp (float): Temperature in Kelvin.

    Returns:
    - float: Dynamic viscosity in kilograms per meter-second.

    Source of lookup table: https://www.me.psu.edu/cimbala/me433/Links/Table_A_9_CC_Properties_of_Air.pdf
    Temperatures converted from source (Celsius to Kelvin).
    """
    # Lookup table for dynamic viscosity
    temps = np.array([173.15, 223.15, 233.15, 243.15, 253.15, 263.15, 273.15, 278.15, 283.15, 288.15, 293.15, 298.15, 303.15, 308.15, 313.15, 318.15, 323.15, 333.15, 343.15])
    viscosities = np.array([1.189e-6, 1.474e-5, 1.527e-5, 1.579e-5, 1.630e-5, 1.680e-5, 1.729e-5, 1.754e-5, 1.778e-5, 1.802e-5, 1.825e-5, 1.849e-5, 1.872e-5, 1.895e-5, 1.918e-5, 1.941e-5, 1.963e-5, 2.008e-5, 2.052e-5])
    
    # Interpolate
    viscosity = np.interp(temp, temps, viscosities)
    return viscosity

def calculate_reynolds_number(air_density, speed, len_characteristic, dynamic_viscosity):
    """
    Calculate the Reynolds number of a solid moving through air.

    Args:
    - air_density (float): The density of the air.
    - speed (float): The relative speed of the solid and the air.
    - len_characteristic (float): The characteristic length of the solid.
    - dynamic_viscosity (float): The dynamic viscosity of the air.

    Returns:
    - float: The Reynolds number of the solid.
    """
    return (air_density * speed * len_characteristic) / dynamic_viscosity

# motor burn curves
    # both likely to either not be used in simulator on the MCU (precompute thrusts and masses at each time given a chosen timestep), or to be rewritten to be more efficient
def mass_at_time(time, dry_mass, fuel_mass_lookup):
    """
    Calculate the total mass of the rocket at a given time during motor burn.

    Args:
    - time (float): Time in seconds since motor ignition.
    - dry_mass (float): Dry mass of the rocket in kilograms.
    - fuel_mass_lookup (dict): Dictionary mapping times to fuel masses.

    Returns:
    - float: Total mass of the rocket at the specified time.
    """
    time_list = list(fuel_mass_lookup.keys())
    lower_time = max([t for t in time_list if t <= time])
    upper_time = min([t for t in time_list if t > time])
    lower_mass = fuel_mass_lookup[lower_time]
    upper_mass = fuel_mass_lookup[upper_time]
    return (dry_mass + lower_mass + (time - lower_time) * (upper_mass - lower_mass) / (upper_time - lower_time))
def thrust_at_time(time, engine_thrust_lookup): 
    """
    Calculate the thrust of the rocket engine at a given time during motor burn.

    Args:
    - time (float): Time in seconds since motor ignition.
    - engine_thrust_lookup (dict): Dictionary mapping times to thrust values.

    Returns:
    - float: Thrust of the engine at the specified time.
    """
    time_list = list(engine_thrust_lookup.keys())
    lower_time = max([t for t in time_list if t <= time])
    upper_time = min([t for t in time_list if t > time])
    lower_thrust = engine_thrust_lookup[lower_time]
    upper_thrust = engine_thrust_lookup[upper_time]
    return lower_thrust + (time - lower_time) * (upper_thrust - lower_thrust) / (upper_time - lower_time)
