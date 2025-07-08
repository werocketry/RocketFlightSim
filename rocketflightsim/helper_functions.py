import numpy as np
from . import constants as con

# atmospheric conditions
def temp_at_altitude(h, reference_temp, lapse_rate = con.T_lapse_rate):
    """
    Calculate the temperature at a given altitude above a reference point. Within the troposphere, temperature decreases linearly with increasing altitude at a rate known as the lapse rate. The lapse rate is typically around 6.5 degrees Celsius per kilometer, but it can vary depending on location, time of year, and other factors.

    Args
    ----
    h : float
        Altitude above the reference point in meters.
    reference_temp : float
        Temperature at the reference altitude in Celsius or Kelvin.
    lapse_rate : float, optional
        Rate at which temperature decreases with increasing altitude in degrees Celsius or Kelvin per meter. Defaults to the standard lapse rate of -0.0065.

    Returns
    -------
    float
        Temperature at the given altitude above the reference point in Celsius or Kelvin (same unit as input).
    """
    return reference_temp + (h * lapse_rate)

def air_density_fn(pressure, temp):
    """
    Calculate the density of air at a given pressure and temperature.

    Args
    ----
    pressure : float
        Pressure in Pascals.
    temp : float
        Temperature in Kelvin.

    Returns
    -------
    float
        Air density in kilograms per cubic meter.
    """
    return pressure / (con.R_specific_air * temp)

def air_density_optimized(temp, multiplier, exponent):
    """
    Calculate the density of air at a given height above a reference point. Optimized function that assumes the temperature lapse rate and force of gravity are constant (as they effectively are in the troposphere) to avoid repeat calculations.

    Args
    ----
    temp : float
        Temperature at the given height above the reference point in Kelvin.
    multiplier : float
        A constant derived from the temperature and pressure at the reference point, the lapse rate, the specific gas constant for air, and the magnitude of the force of gravity. Calculated at initialization of Environment objects. Equal to P_launchpad / (R_air * pow(T_launchpad, - F_gravity / (R_air * T_lapse_rate))).
    exponent : float
        A constant derived from the lapse rate, the specific gas constant for air, and the magnitude of the force of gravity. Calculated at initialization of Environment objects. Equal to - F_gravity / (R_air * T_lapse_rate) - 1.

    Returns
    -------
    float
        Air density at the given height in kilograms per cubic meter.
    """
    return multiplier * pow(temp, exponent)

# aerodynamics
def calculate_dynamic_pressure(fluid_density, speed):
    """
    Calculate the dynamic pressure imparted on a solid moving through a fluid.

    Args
    ----
    fluid_density : float
        Density of the fluid.
    speed : float
        Relative speed between the solid and the fluid.

    Returns
    -------
    float
        Dynamic pressure on the solid.
    """
    return 0.5 * fluid_density * (speed ** 2)

def mach_number_fn(v, temp):
    """
    Calculate the Mach number of an object moving through air at a given temperature.

    Args
    ----
    v : float
        Velocity of the object relative to the air in meters per second.
    temp : float
        Air temperature in Kelvin.

    Returns
    -------
    float
        Mach number (dimensionless).
    """
    return v / np.sqrt(con.adiabatic_index_air_times_R_specific_air * temp)

# gravity
def get_local_gravity(latitude, h = 0):
    """
    Calculate the acceleration due to gravity at a given latitude and altitude above sea level.

    Args
    ----
    latitude : float
        Latitude in degrees.
    h : float
        Elevation above sea level in meters. Defaults to 0.

    Returns
    -------
    float
        Acceleration due to gravity in meters per second squared.

    References
    ----------
    Based on the International Gravity Formula 1980 (IGF80) model, as outlined in https://en.wikipedia.org/wiki/Theoretical_gravity#International_gravity_formula_1980
    """
    latitude = np.abs(latitude) # The formula is symmetric about the equator (like the oblate spheroid Earth)

    phi = np.deg2rad(latitude)

    # Coefficients for the gravity formula for the Earth as an oblate spheroid
    gamma_a = 9.780327  # m/s^2
    c1 = 0.0052790414
    c2 = 0.0000232718
    c3 = 0.0000001262
    c4 = 0.0000000007

    gamma_0 = gamma_a * (1 + c1 * np.sin(phi)**2 + c2 * np.sin(phi)**4 + c3 * np.sin(phi)**6 + c4 * np.sin(phi)**8)

    # Coefficients for the free air correction (the correction for the height above sea level)
    k1 = 3.15704e-07  # 1/m
    k2 = 2.10269e-09  # 1/m
    k3 = 7.37452e-14  # 1/m^2

    return gamma_0 * (1 - (k1 - k2 * np.sin(phi)**2) * h + k3 * h**2)

def average_gravity(latitude, h_0 = 0, h_1 = None):
    """
    Calculate the average acceleration due to gravity between two altitudes above sea level.

    Args
    ----
    latitude : float
        Latitude in degrees.
    h_0 : float
        Elevation of the first altitude above sea level in meters. Defaults to 0.
    h_1 : float
        Elevation of the second altitude above sea level in meters. Defaults to None, in which case the function will return the acceleration due to gravity at the first altitude instead of the average.

    Returns
    -------
    float
        Average acceleration due to gravity in meters per second squared.

    Notes
    -----
    This function averages the force of gravity as a function of altitude, which is not as accurate as averaging the force of gravity as a function of time for a rocket flight simulation. However, the latter is more computationally expensive and is not necessary for most simulations. This function is a compromise between accuracy and efficiency for sounding rockets that go to extreme altitudes.

    At the top of the troposphere (an average altitude of 13km ASL), the force of gravity is about 0.5% weaker than at the Earth's surface. At the Kármán line (100km ASL), the force of gravity is about 3% weaker than at the Earth's surface. For rockets made by most hobbyists and school teams, the difference in force of gravity between the launchpad and the expected apogee is negligible, and the using the get_local_gravity function is sufficient.

    # TODO Maybe add a flight function that calculates the force of gravity over time if it's desired to simulate rockets that fly to a very high altitude.
    """
    g_0 = get_local_gravity(latitude, h_0)
    if h_1:
        g_1 = get_local_gravity(latitude, h_1)
        return (g_0 + g_1) / 2
    else:
        return g_0

# not used in simulator
def pressure_at_altitude(h, reference_temp, reference_pressure, lapse_rate = con.T_lapse_rate, F_gravity = con.F_gravity):
    """
    Calculate the air pressure at a given altitude above a reference point.

    Args
    ----
    h : float
        Altitude above the reference point in meters.
    reference_temp : float
        Temperature at the reference point in Kelvin.
    reference_pressure : float
        Air pressure at the reference point in Pascals.
    lapse_rate : float, optional
        Rate at which temperature decreases with increasing altitude in Kelvin per meter. Defaults to the standard lapse rate of 0.0065 K/m.
    F_gravity : float, optional
        Magnitude of the force of gravity in Newtons. Defaults to the standard value of 9.80665 N.

    Returns
    -------
    float
        Air pressure at the given altitude in Pascals.
    """
    return reference_pressure * pow(
        (1 - (h * lapse_rate / reference_temp)),
        (F_gravity / (con.R_specific_air * lapse_rate))
    )

def lookup_dynamic_viscosity(temp):
    """
    Look up the dynamic viscosity of air at a given temperature.

    Args
    ----
    temp : float
        Temperature in Kelvin.

    Returns
    -------
    float
        Dynamic viscosity in kilograms per meter-second.

    References
    ----------
    Source of lookup table: https://www.me.psu.edu/cimbala/me433/Links/Table_A_9_CC_Properties_of_Air.pdf
    Temperatures converted from source (Celsius to Kelvin).
    """
    # Lookup table for dynamic viscosity
    temps = np.array([173.15, 223.15, 233.15, 243.15, 253.15, 263.15, 273.15, 278.15, 283.15, 288.15, 293.15, 298.15, 303.15, 308.15, 313.15, 318.15, 323.15, 333.15, 343.15])
    viscosities = np.array([1.189e-6, 1.474e-5, 1.527e-5, 1.579e-5, 1.630e-5, 1.680e-5, 1.729e-5, 1.754e-5, 1.778e-5, 1.802e-5, 1.825e-5, 1.849e-5, 1.872e-5, 1.895e-5, 1.918e-5, 1.941e-5, 1.963e-5, 2.008e-5, 2.052e-5])
    
    # Interpolate to find dynamic viscosity at the given temperature
    return np.interp(temp, temps, viscosities)

def calculate_reynolds_number(fluid_density, speed, len_characteristic, dynamic_viscosity):
    """
    Calculate the Reynolds number of a solid moving through a fluid.

    Args
    ----
    fluid_density : float
        Density of the fluid.
    speed : float
        Relative speed between the solid and the fluid.
    len_characteristic : float
        Characteristic length of the solid.
    dynamic_viscosity : float
        Dynamic viscosity of the fluid.

    Returns
    -------
    float
        Reynolds number of the solid moving through the fluid.
    """
    return fluid_density * speed * len_characteristic / dynamic_viscosity

# motor burn curves TODO: look at improving efficiency
    # both likely to either not be used in simulator on the MCU (precompute thrusts and masses at each time given a chosen timestep), or to be rewritten to be more efficient
def mass_at_time(time, dry_mass, fuel_mass_lookup):
    """
    Calculate the total mass of the rocket at a given time during motor burn.

    Args
    ----
    time : float
        Time in seconds since motor ignition.
    dry_mass : float
        Dry mass of the rocket in kilograms.
    fuel_mass_lookup : dict
        Dictionary mapping times to fuel masses.

    Returns
    -------
    float
        Total mass of the rocket at the specified time.
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

    Args
    ----
    time : float
        Time in seconds since motor ignition.
    engine_thrust_lookup : dict
        Dictionary mapping times to thrust values.

    Returns
    -------
    float
        Thrust of the engine at the specified time.
    """
    time_list = list(engine_thrust_lookup.keys())
    lower_time = max([t for t in time_list if t <= time])
    upper_time = min([t for t in time_list if t > time])
    lower_thrust = engine_thrust_lookup[lower_time]
    upper_thrust = engine_thrust_lookup[upper_time]
    return lower_thrust + (time - lower_time) * (upper_thrust - lower_thrust) / (upper_time - lower_time)
