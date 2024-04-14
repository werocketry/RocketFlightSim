# flight data from other teams to test the simulator

import numpy as np
import rocket_classes
import constants as con

""" Notre Dame Rocket Team Rocket 2020
https://github.com/RocketPy-Team/RocketPy/blob/master/docs/examples/ndrt_2020_flight_sim.ipynb
"""

Cesaroni_4895L1395_P = rocket_classes.Motor(
    # https://www.thrustcurve.org/simfiles/5f4294d20002e90000000614/
    dry_mass = 1.958,
    thrust_curve = {
        0: 0,
        0.02: 100,
        0.04: 1400,
        0.1: 1800,
        0.2: 1500,
        0.4: 1540,
        0.8: 1591,
        1.1: 1641,
        2.4: 1481,
        2.8: 1446,
        3: 1500,
        3.18: 830,
        3.35: 100,
        3.45: 0
    },
    fuel_mass_curve = {
        0: 2.475,
        0.02: 2.47449,
        0.04: 2.46691,
        0.1: 2.41837,
        0.2: 2.33495,
        0.4: 2.18124,
        0.8: 1.86462,
        1.1: 1.6195,
        2.4: 0.593463,
        2.8: 0.297477,
        3: 0.148524,
        3.18: 0.0424968,
        3.35: 0.00252806,
        3.45: 0
    }
)
NDRT_2020 = rocket_classes.Rocket(
    # as per parameters in the GitHub
    rocket_mass = 18.998,
    motor = Cesaroni_4895L1395_P,
    A_rocket = np.pi * 0.1015 ** 2,
    Cd_rocket_at_Ma = 0.44
)
NDRT_2020_launch_conditions = rocket_classes.LaunchConditions(
    # as per parameters in the GitHub, and using RocketPy to get launchpad pressure and temp from their weather data file (https://github.com/RocketPy-Team/RocketPy/blob/master/tests/fixtures/acceptance/NDRT_2020/ndrt_2020_weather_data_ERA5.nc)
    launchpad_pressure = 99109,
    launchpad_temp = 278.03-273.15,
    L_launch_rail = 3.353,
    launch_angle = 90
)



import flight_simulation as fsim
apogee = fsim.simulate_flight(NDRT_2020, NDRT_2020_launch_conditions, timestep = 0.01)[0]['height'].iloc[-1]
print(f"NDRT 2020 prediction: {apogee} m")
print(f"Actual apogee: 1317 m")
print(f"Error: {apogee - 1317}")
print(f"Percent error: {(apogee - 1317)/1317*100} %")
# note that the sim doesn't account for wind yet (5.66 m/s), will bring predicted apogee down

# plot the flight
import plotting_functions as pf
(
        dataset,
        liftoff_index,
        launch_rail_cleared_index,
        burnout_index,
        apogee_index,
) = fsim.simulate_flight(NDRT_2020, NDRT_2020_launch_conditions, timestep = 0.01)

time = dataset["time"][:apogee_index]
height = dataset["height"][:apogee_index].copy()
speed = dataset["speed"][:apogee_index].copy()
v_y = dataset["v_y"][:apogee_index].copy()
a_y = dataset["a_y"][:apogee_index].copy()
a_x = dataset["a_x"][:apogee_index].copy()
g_force = np.sqrt(a_y**2 + a_x**2) / con.F_gravity

pf.plot_aerodynamics(        
        time,
        height,
        speed,
        dataset["q"],
        dataset["angle_to_vertical"],
        dataset["air_density"],)