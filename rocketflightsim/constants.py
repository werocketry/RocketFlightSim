# Constants 
R_universal = 8.3144598  # universal gas constant, J/(mol*K)
MM_air = 0.0289644  # molar mass of air, kg/mol
adiabatic_index_air = 1.4  # unitless
"""Notes on adiabatic index (also known as the heat capacity ratio or ratio of specific heats (cp/cv)) for air

As per https://www.grc.nasa.gov/WWW/BGH/realspec.html, air is calorically perfect up to low supersonic Mach numbers, so the adiabatic index doesn't change with airspeed over the speeds that most hobbyist or collegiate team rockets will experience. 

As a function of teperature, for dry air, the adiabatic index according to different sources is:
    https://en.wikipedia.org/wiki/Heat_capacity_ratio
    
        - 1.404 at -15°C
        - 1.403 at 0°C
        - 1.400 at 20°C
        - 1.398 at 200°C

    https://www.chemeurope.com/en/encyclopedia/Heat_capacity_ratio.html

        - 1.403 at 0°C
        - 1.400 at 20°C
        - 1.401 at 100°C

The value of 1.4 is a very good approximation for the temperature ranges that most hobbyist or collegiate team rockets will experience.
"""

# Derived constants
R_specific_air = R_universal / MM_air  # J/(kg*K)
adiabatic_index_air_times_R_specific_air = adiabatic_index_air * R_specific_air  # J/(kg*K)

# Conversion factors
ft_to_m_conversion = 0.3048 # m/ft
m_to_ft_conversion = 1/ft_to_m_conversion  # ft/m

# Default launch site values. Specific launch site values can be set in LaunchConditions objects
F_gravity = 9.80665  # m/s^2
T_lapse_rate = -0.0065  # K/m

# Default timestep for the simulation
default_timestep = 0.02
""" Notes on timesteps:

The default for OpenRocket sims is 0.01s for the first while, and then somewhere between 0.02 and 0.05 for a while, and then 0.05 for most of the rest of the ascent. It simulates more complicated dynamics than we do

A timestep of 0.02s gives apogees a difference of a few feet for a 10k launch compared to using 0.001s. 0.001s can still be used for one-off sims, but when running many sims, 0.02s is better.
TODO: check that again when done splitting the sim into stages
"""