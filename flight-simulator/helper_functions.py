import numpy as np
import constants as con

# aerodynamics

def temp_at_height(h, launchpad_temp):
    """
    Calculate the temperature at a given height above the launchpad.

    Args:
    - h (float): Height above the launchpad in meters.
    - launchpad_temp (float): Temperature at the launchpad in Celsius or Kelvin.

    Returns:
    - float: Temperature at the given height in Celsius or Kelvin (same as input).
    """
    return launchpad_temp - (h * con.T_lapse_rate)
def pressure_at_height(h, launchpad_temp, launchpad_pressure):
    """
    Calculate the air pressure at a given height above the launchpad.

    Args:
    - h (float): Height above the launchpad in meters.
    - launchpad_temp (float): Temperature at the launchpad in Kelvin.
    - launchpad_pressure (float): Air pressure at the launchpad in Pascals.

    Returns:
    - float: Air pressure at the given height in Pascals.
    """
    return launchpad_pressure * pow(
        (1 - (h * con.T_lapse_rate / launchpad_temp)),
        (con.F_g_over_R_spec_air_T_lapse_rate)
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
def air_density_optimized(temp, multiplier):
    """
    Calculate the density of air at a given height above the launchpad.

    Args:
    - temp (float): Temperature at the given height in Kelvin.
    - multiplier (float): A constant derived from the temperature and pressure at the launchpad, the lapse rate, the specific gas constant for air, and the value for gravity near the Earth's surface. Calculated at the start of the simulation script outside of the main loops. Equal to P_launchpad / (R_air * pow(T_launchpad, Fg_over_R_spec_air_T_lapse_rate)).

    Returns:
    - float: Air density at the given height in kilograms per cubic meter.
    """
    return multiplier * pow(temp, con.F_g_over_R_spec_air_T_lapse_rate_minus_one)
# TODO: check if exponential approximation gives a negligible error (https://en.wikipedia.org/wiki/Density_of_air), if so, maybe could use it at leat in the controller sim

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
    Calculate the Mach number of an object moving in air at a given temperature.

    Args:
    - v (float): Velocity in meters per second.
    - temp (float): Temperature in Kelvin.

    Returns:
    - float: Mach number (dimensionless).
    """
    return v / np.sqrt(con.adiabatic_index_air_times_R_specific_air * temp)

# not used anymore
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
    # both likely to either not be used in simulator on the MCU, or to be rewritten to be more efficient
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
