import sys
import os

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rocketflightsim.rocket_classes import Motor, Rocket, LaunchConditions, Airbrakes

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
    rocket_mass = 14, # kg
    motor = Cesaroni_7579M1520_P,
    Cd_rocket_at_Ma = 0.4,
    h_second_rail_button = 0.8  # m
)

# LaunchConditions class configuration for Spaceport America Cup
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
    - the closest station to SC was Datil, which had a lapse rate of -3.1 K/km
"""
L_launch_rail_ESRA_provided_SAC = 5.18  # m, 
""" ESRA provides teams with a 5.18m rail at competition """
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
launch_rail_elevation_SAC = 86  # deg from horizontal
""" How the standard launch angle at Spaceport America Cup was determined

ESRA changed it to 86° for 2024, as noted in the forum:
https://www.herox.com/SpaceportAmericaCup2024/forum/thread/11118

Teams have noted that they've been told to use angles at least as low as 80°. The Range Safety Officer picks the angle based on various factors, including the rocket being launched, the weather, and the location of the launch pad. In the design, simulation, and testing phases, use the nominal angle of 86°, but consider the possibility of the launch angle being more or less than that on competition day.

Previously, the standard launch angle was 84°, as noted in the DTEG:
DTEG 10.1.1: 
    > Launch vehicles will nominally launch at an elevation angle of 84° ±1°
DTEG 10.1.2:
    > Range Safety Officers reserve the right to require certain vehicles’ launch elevation be lower or higher if flight safety issues are identified during pre-launch activities
"""

Spaceport_America_avg_launch_conditions = LaunchConditions(
    launchpad_pressure = launchpad_pressure_SAC,
    launchpad_temp = launchpad_temp_SAC,
    L_launch_rail = L_launch_rail_ESRA_provided_SAC,
    launch_rail_elevation = launch_rail_elevation_SAC,
    local_T_lapse_rate = T_lapse_rate_SA,
    latitude = latitude_SA,
    altitude = altitude_SA
)

# Default airbrakes model
default_airbrakes_model = Airbrakes(
    num_flaps = 3,
    A_flap = 0.004,  # m^2  flap area
    Cd_brakes = 1,
    max_deployment_angle = 45,  # deg
    max_deployment_rate = 5,  # deg/s
    max_retraction_rate = 10 # deg/s
)

if __name__ == "__main__":
    from rocketflightsim.flight_simulation import simulate_flight
    from rocketflightsim.tools.plotting_functions import plot_ascent, plot_aerodynamics, plot_airbrakes_ascent

    dataset, liftoff_index, launch_rail_cleared_index, burnout_index, apogee_index = simulate_flight(rocket = example_rocket, launch_conditions = Spaceport_America_avg_launch_conditions, timestep = 0.001)
    print(f"Motor burnout: \n\tHeight: {dataset['z'].iloc[burnout_index - 1]} m\n\tSpeed: {dataset['airspeed'].iloc[burnout_index - 1]} m/s\n\tTime: {dataset['time'].iloc[burnout_index - 1]} s\n")
    print(f"Apogee: \n\tHeight: {dataset['z'].iloc[apogee_index - 1]} m\n\tTime: {dataset['time'].iloc[apogee_index - 1]} s\n")

    plot_ascent(dataset['time'], dataset['z'], dataset['airspeed'], dataset['v_z'], dataset['a_z'])