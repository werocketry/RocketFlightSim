import sys
import os

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rocketflightsim.classes.motor import Motor
from rocketflightsim.classes.rocket import Rocket
from rocketflightsim.classes.environment import Environment
from rocketflightsim.classes.launchpad import Launchpad
from rocketflightsim.classes.airbrakes import Airbrakes
import rocketflightsim.constants as con

# Example motor configurations
Cesaroni_7579M1520_P = Motor(
    # source: https://www.thrustcurve.org/simfiles/5f4294d20002e900000006b1/
    dry_mass = 2.981,
    thrust_curve = {
        0: 0,
        0.04: 1427.8,
        0.082: 1706.39,
        0.176: 1620.49,
        0.748: 1734.25,
        1.652: 1827.11,
        2.676: 1715.68,
        3.89: 1423.15,
        4.399: 1404.58,
        4.616: 661.661,
        4.877: 69.649,
        4.897: 0
    },
    fuel_mass_curve = {
        0: 3.737,
        0.04: 3.72292,
        0.082: 3.69047,
        0.176: 3.61337,
        0.748: 3.14029,
        1.652: 2.34658,
        2.676: 1.45221,
        3.89: 0.512779,
        4.399: 0.157939,
        4.616: 0.0473998,
        4.877: 0.000343417,
        4.897: 0
    }
)

Cesaroni_7450M2505_P = Motor(
    dry_mass = 2.866, # source: http://www.pro38.com/products/pro98/motor/MotorData.php?prodid=7450M2505-P
    thrust_curve = { # source: https://www.thrustcurve.org/simfiles/5f4294d20002e900000005a0/
        0: 0,
        0.12: 2600,
        0.21: 2482,
        0.6: 2715,
        0.9: 2876,
        1.2: 2938,
        1.5: 2889,
        1.8: 2785,
        2.1: 2573,
        2.4: 2349,
        2.7: 2182,
        2.99: 85,
        3: 0
    },
    fuel_mass_curve = { # source: https://www.thrustcurve.org/simfiles/5f4294d20002e900000005a0/
        0: 3.423,
        0.12: 3.35069,
        0.21: 3.24469,
        0.6: 2.77495,
        0.9: 2.38622,
        1.2: 1.98198,
        1.5: 1.57684,
        1.8: 1.18234,
        2.1: 0.809811,
        2.4: 0.467594,
        2.7: 0.152563,
        2.99: 0.000196996,
        3: 0
    }
)

# Example rocket configuration
example_rocket = Rocket(
    A_rocket = 0.015326, # m^2
    rocket_mass = 15, # kg
    motor = Cesaroni_7579M1520_P,
    Cd_rocket = 0.4,
    h_second_rail_button = 0.8  # m
)

# Example airbrakes model
example_airbrakes_model = Airbrakes(
    num_flaps = 3,
    A_flap = 0.004,  # m^2  flap area
    Cd_brakes = 1,
    max_deployment_angle = 45,  # deg
    max_deployment_rate = 5,  # deg/s
    max_retraction_rate = 10 # deg/s
)


# TODO split the competition environments into a separate file?
# Environment class configuration for Spaceport America Cup
T_lapse_rate_SA = -0.00817  # K/m
""" How T_lapse_rate at Spaceport America was determined

Only one source was found with the lapse rate for Spaceport America:
    - https://egusphere.copernicus.org/preprints/2023/egusphere-2023-633/egusphere-2023-633.pdf
    - luckily, they took their measurements in June
    - The lapse rates for the stratosphere for each of three flights were reported as follows:
        - June 1st 2021 -8.4 K/km
        - June 4th 2021 -7.9 K/km
        - June 6th 2021 -8.2 K/km
    - An average of these is what was chosen for the simulation
    - The linear lapse rate was valid for the first 10 km AGL

For future reference, it should be noted that time of year has a large effect on the lapse rate, as reported in:
    - https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-00162/article_deploy/remotesensing-14-00162.pdf?version=1640917080
    - https://hwbdocs.env.nm.gov/Los%20Alamos%20National%20Labs/TA%2004/2733.PDF
        - states that the average lapse rate in NM is:
            - -4.0F/1000ft (-7.3 K/km) in July
            - -2.5F/1000ft (-4.6 K/km) in January
        - -8.2 K/km is higher than the summer average, but generally desert areas have higher-than-normal lapse rates

The following was the most comprehensive source found for temperature lapse rates in New Mexico: 
- https://pubs.usgs.gov/bul/1964/report.pdf
- No values were found for Spaceport itself, but values for other locations in New Mexico were found
- the report says that in the western conterminous United States, temperature lapse rates are generally significantly less than the standard -6.5 K/km
- the report didn't include the date (or month) of the measurements, so I'd assume that it happened in the winter due to the low lapse rates, and/or the data being several decades old means that it's no longer as accurate due to the changing global climate
- has values for many locations in New Mexico (search for n. mex), and they ranged from -1.4 to -3.9 K/km
    - the closest station to SA was Datil, which had a lapse rate of -3.1 K/km
"""
launchpad_pressure_SAC = 86400  # Pa
""" How the launchpad pressure at Spaceport America was determined

- 86400 2022/06/24   WE Rocketry 2022 TeleMega/TeleMetrum data
- 86405 2022/06/23   https://github.com/ISSUIUC/flight-data/tree/master/20220623
- 86170 2023/06/21   https://github.com/ISSUIUC/flight-data/tree/master/20230621
"""
launchpad_temp_SAC = 35  # deg C
""" Ground-level temperature at Spaceport America Cup note

Flights can occur between about 07:00 and 16:30 local time, so the temperature at the time of launch can vary significantly. 35 C is about what it has been historically during the competition in mid-late June. Getting closer to launch day, it would be more accurate to use a weather forecast to get a value for expected temperature(s).

You can also consider running simulations with a range of temperatures that have been seen on launch days in the past (normally between 25 and 45 C) to see how different ground-level temperatures could affect a rocket's flight.
"""
latitude_SA = 32.99  # deg, Spaceport America's latitude
""" https://maps.app.goo.gl/rZT6MRLqHneA7wNX7 """
altitude_SA = 1401  # m, Spaceport America's elevation
""" https://www.spaceportamerica.com/faq/#toggle-id-15 """

Spaceport_America_Cup_avg_environment = Environment(
    launchpad_pressure = launchpad_pressure_SAC,
    launchpad_temp = launchpad_temp_SAC,
    local_T_lapse_rate = T_lapse_rate_SA,
    latitude = latitude_SA,
    altitude = altitude_SA
)

# Launchpad class configuration for Spaceport America Cup
rail_length_ESRA_provided_SAC = 17 * con.ft_to_m_conversion  # m
""" ESRA provides teams with a 5.18m rail at competition """
launch_rail_elevation_SAC = 86  # deg from horizontal
""" Notes on the standard launch angle at Spaceport America Cup

ESRA changed it to 86° for 2024, as noted in the forum:
https://www.herox.com/SpaceportAmericaCup2024/forum/thread/11118

Teams have noted that they've been told to use angles at least as low as 80°. The Range Safety Officer picks the angle based on various factors, including the rocket being launched, the weather, and the location of the launch pad. In the design, simulation, and testing phases, use the nominal angle of 86°, but consider the possibility of the launch angle being more or less than that on competition day.

Previously, the standard launch angle was 84°, as noted in the DTEG:
DTEG 10.1.1: 
    > Launch vehicles will nominally launch at an elevation angle of 84° ±1°

TODO 2025 DTEG says 86° ±2°. Ask ESRA if they changed it back?

DTEG 10.1.2:
    > Range Safety Officers reserve the right to require certain vehicles’ launch elevation be lower or higher if flight safety issues are identified during pre-launch activities
"""

Spaceport_America_Cup_default_launchpad = Launchpad(
    rail_length = rail_length_ESRA_provided_SAC,
    launch_rail_elevation = launch_rail_elevation_SAC
)

# Environment class configuration for Launch Canada
T_lapse_rate_LC = con.T_lapse_rate
""" How T_lapse_rate at Launch Canada was determined

From a really really rough analysis of the flight data here: https://github.com/UVicRocketry/Xenia1-MaGP-I/tree/main

The temperature readings couldn't be used because it looks like the flight computer never got to the temperature of the outside (unless it only dropped 4 degrees on a 10k ft flight). However, looking at the pressure data, it looks similar to what it should look like given a lapse rate quite close to the standard -6.5 K/km. This is a very rough estimate, and it would be better to get a more accurate value from real temperature measurements at the launch site around late August.
"""
launchpad_pressure_LC = 102000  # Pa
""" Ground-level pressure at Launch Canada note

I could not find historical weather data for the launch site itself. Camp Kenogaming is very close to the launch site (6km away) and at nearly the same elevation: https://www.timeanddate.com/weather/@5914408/historic?month=8&year=2024
"""
launchpad_temp_LC = 20  # deg C
""" Ground-level temperature at Launch Canada note

I could not find historical weather data for the launch site itself. Camp Kenogaming is very close to the launch site (6km away) and at nearly the same elevation: https://www.timeanddate.com/weather/@5914408/historic?month=8&year=2024

Flights can occur from fairly early in the morning to late in the afternoon, so the temperature at the time of launch can vary significantly. Getting closer to launch day, it would be more accurate to use a weather forecast to get a value for expected temperature(s).

You can also consider running simulations with a range of temperatures that have been seen on launch days in the past (normally between 15 and 30 C) to see how different ground-level temperatures could affect a rocket's flight.
"""
latitude_LC = 47.987 # deg, Launch Canada's launch site latitude
""" https://maps.app.goo.gl/n76cD331j7LiQiTB6 """
altitude_LC = 364 # m, Launch Canada's launch site elevation
""" from Google Earth 
https://earth.google.com/web/search/Launch+Canada+Launch+Pad/@47.9869503,-81.8485488,363.96383335a,679.10907018d,35y """

Launch_Canada_avg_environment = Environment(
    launchpad_pressure = launchpad_pressure_LC,
    launchpad_temp = launchpad_temp_LC,
    local_T_lapse_rate = T_lapse_rate_LC,
    latitude = latitude_LC,
    altitude = altitude_LC
)

# Launchpad class configuration for Launch Canada
rail_length_provided_LC = 18.5 * con.ft_to_m_conversion # m
launch_rail_elevation_LC = 84 # deg from horizontal
""" DTEG """

Launch_Canada_default_launchpad = Launchpad(
    rail_length = rail_length_provided_LC,
    launch_rail_elevation = launch_rail_elevation_LC
)