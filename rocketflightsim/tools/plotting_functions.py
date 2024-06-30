# TODO: do a major refresh of these (consider deleting them?)

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .. import constants as con
from .. import helper_functions as hfunc


def plot_ascent(time, z, airspeed, v_z, a_z, unit="m"):
    """
    Plot ascent data including height, airspeed, and vertical acceleration.

    Args:
    - time (pd.Series): Time series data.
    - z (pd.Series): Height series data.
    - airspeed (pd.Series): Airspeed series data.
    - v_z (pd.Series): Vertical velocity series data.
    - a_z (pd.Series): Vertical acceleration series data.
    - unit (str): Unit of measurement for height, airspeed, etc.
    """
    fig, ax1 = plt.subplots()
    ax1.plot(time, z, color="b")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel(f"Height ({unit})", color="b")
    ax1.tick_params(axis="y", labelcolor="b")

    ax2 = ax1.twinx()
    ax2.plot(time, v_z, color="r")
    ax2.set_ylabel(f"Vertical velocity ({unit}/s)", color="r")
    ax2.tick_params(axis="y", labelcolor="r")

    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.plot(time, a_z, color="g")
    ax3.set_ylabel(f"Vertical acceleration ({unit}/s^2)", color="g")
    ax3.tick_params(axis="y", labelcolor="g")

    plt.title("Ascent Overview")
    plt.show()


def plot_aerodynamics(time, z, airspeed, q, angle_to_vertical, air_density, unit="m"):
    """
    Plot aerodynamic parameters over the ascent.

    Args:
    - time (pd.Series): Time series data.
    - z (pd.Series): Height series data.
    - airspeed (pd.Series): Airspeed series data.
    - q (pd.Series): Dynamic pressure series data.
    - angle_to_vertical (pd.Series): Angle to vertical series data.
    - air_density (pd.Series): Air density series data.
    - unit (str): Unit of measurement for height, airspeed, etc.
    """
    fig, ax1 = plt.subplots()
    ax1.plot(time, z, color="b", label="Height")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel(f"Height ({unit})", color="b")
    ax1.tick_params(axis="y", labelcolor="b")
    ax1.set_ylim(0, z.max() * 1.1)

    ax2 = ax1.twinx()
    ax2.plot(time, airspeed, color="r", label="Speed")
    ax2.set_ylabel(f"Speed ({unit}/s)", color="r")
    ax2.tick_params(axis="y", labelcolor="r")
    ax2.set_ylim(0, airspeed.max() * 1.1)

    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.plot(time, q / 1000, color="g", label="q")
    ax3.set_ylabel("q (kPa)", color="g")
    ax3.tick_params(axis="y", labelcolor="g")
    ax3.set_ylim(0, q.max() / 1000 * 1.1)

    ax4 = ax1.twinx()
    ax4.spines["right"].set_position(("outward", 120))
    ax4.plot(time, angle_to_vertical * 180 / np.pi, color="c", label="Angle to Vertical")
    ax4.set_ylabel(f"Angle to vertical (deg)", color="c")
    ax4.tick_params(axis="y", labelcolor="c")
    
    ax4.set_yticks(range(0, 91, 15))
    ax4.set_ylim(0, angle_to_vertical.max() * 180 / np.pi * 1.1)

    ax5 = ax1.twinx()
    ax5.spines["right"].set_position(("outward", 180))
    ax5.plot(time, air_density, color="m", label="Air Density")
    ax5.set_ylabel("Air Density (kg/m^3)", color="m")
    ax5.tick_params(axis="y", labelcolor="m")

    plt.title("Aerodynamics during Ascent")
    plt.show()


def plot_airbrakes_ascent(ascent, airbrakes, unit="m"):
    """
    Plot ascent data including height, airspeed, acceleration, deployment angle, and force on airbrakes.

    Args:
    - ascent (pd.DataFrame): Dataframe containing the ascent data with airbrakes.
    - unit (str): Unit of measurement for height, airspeed, etc.
    """

    # Existing code for height, airspeed, and acceleration plots
    z = (
        ascent["z"].copy() * con.m_to_ft_conversion
        if unit == "ft"
        else ascent["z"].copy()
    )
    airspeed = (
        ascent["airspeed"].copy() * con.m_to_ft_conversion
        if unit == "ft"
        else ascent["airspeed"].copy()
    )
    accel = (
        ascent["a_z"].copy() * con.m_to_ft_conversion
        if unit == "ft"
        else ascent["a_z"].copy()
    )

    # New code to calculate force
    # Assuming 'ascent' DataFrame includes 'q' and 'deployment_angle'
    # and 'airbrake_deployment' is defined or calculated before this function
    force = (ascent["q"]) * airbrakes.A_flap * np.sin(ascent["deployment_angle"]) * 3

    fig, ax1 = plt.subplots()

    # Existing plotting code for height, airspeed, acceleration, and deployment angle
    ax1.plot(ascent["time"], z, color="b")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel(f"Height ({unit})", color="b")
    ax1.tick_params(axis="y", labelcolor="b")
    ax1.axhline(y=10000, color='gray', linestyle='--')

    ax2 = ax1.twinx()
    ax2.plot(ascent["time"], airspeed, color="r")
    ax2.set_ylabel(f"Speed ({unit}/s)", color="r")
    ax2.tick_params(axis="y", labelcolor="r")

    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.plot(ascent["time"], accel, color="g")
    ax3.set_ylabel(f"Acceleration ({unit}/s^2)", color="g")
    ax3.tick_params(axis="y", labelcolor="g")

    ax4 = ax1.twinx()
    ax4.spines["right"].set_position(("outward", 120))
    ax4.plot(ascent["time"], np.rad2deg(ascent["deployment_angle"]), color="y")
    ax4.set_ylabel(f"Deployment Angle (deg)", color="y")
    ax4.tick_params(axis="y", labelcolor="y")
    ax4.set_yticks(range(0, 46, 15))

    # New plotting code for force
    ax5 = ax1.twinx()
    ax5.spines["right"].set_position(("outward", 180))  # Adjust this as needed
    ax5.plot(ascent["time"], force, color="m")  # 'm' for magenta, can choose any color
    ax5.set_ylabel("Force (N)", color="m")  # Assuming force is in Newtons
    ax5.tick_params(axis="y", labelcolor="m")

    plt.title("Ascent with Airbrakes")
    plt.show()


def display_apogee_parameters_table(ascent, parameters_at_flight_events, unit="m"):
    """
    Display a table of parameters at apogee, including comparisons between ascent with and without airbrakes.

    Args:
    - ascent (pd.DataFrame): Dataframe containing the ascent data with airbrakes.
    - parameters_at_flight_events (pd.DataFrame): Dataframe containing parameters at key flight events.
    - unit (str): Unit of length.
    """
    # Calculate the relevant parameters for ascent with airbrakes
    last_index = len(ascent) - 1
    time_with_airbrakes = ascent["time"].iloc[last_index]
    height_with_airbrakes = (
        ascent["z"].iloc[last_index] * con.m_to_ft_conversion
        if unit == "ft"
        else ascent["z"].iloc[last_index]
    )
    speed_with_airbrakes = (
        ascent["airspeed"].iloc[last_index] * con.m_to_ft_conversion
        if unit == "ft"
        else ascent["airspeed"].iloc[last_index]
    )
    accel_with_airbrakes = (
        ascent["a_z"].iloc[last_index] * con.m_to_ft_conversion
        if unit == "ft"
        else ascent["a_z"].iloc[last_index]
    )
    g_force_with_airbrakes = abs(ascent["a_z"].iloc[last_index] / con.F_gravity)

    # Extract parameters at apogee without airbrakes
    time_without_airbrakes = parameters_at_flight_events.loc["Apogee", "Time (s)"]
    height_without_airbrakes = parameters_at_flight_events.loc[
        "Apogee", f"Height ({unit})"
    ]
    speed_without_airbrakes = parameters_at_flight_events.loc[
        "Apogee", f"Speed ({unit}/s)"
    ]
    accel_without_airbrakes = parameters_at_flight_events.loc[
        "Apogee", f"Vertical accel ({unit}/s^2)"
    ]
    g_force_without_airbrakes = parameters_at_flight_events.loc[
        "Apogee", f"G-force (g)"
    ]

    # Create DataFrame for comparison
    parameters_at_apogee = pd.DataFrame(
        {
            "Time (s)": [time_with_airbrakes, time_without_airbrakes],
            f"Height ({unit})": [height_with_airbrakes, height_without_airbrakes],
            f"Speed ({unit}/s)": [speed_with_airbrakes, speed_without_airbrakes],
            f"Accel ({unit}/s^2)": [accel_with_airbrakes, accel_without_airbrakes],
            f"G-force (g)": [g_force_with_airbrakes, g_force_without_airbrakes],
        },
        index=["Apogee with Airbrakes", "Apogee without Airbrakes"],
    )

    # Calculate deltas and percentage deltas
    delta_values = (
        parameters_at_apogee.loc["Apogee with Airbrakes"]
        - parameters_at_apogee.loc["Apogee without Airbrakes"]
    )
    parameters_at_apogee.loc["Delta"] = delta_values
    percent_delta_values = round(
        delta_values / parameters_at_apogee.loc["Apogee without Airbrakes"] * 100, 2
    )
    parameters_at_apogee.loc["% Delta"] = percent_delta_values

    return parameters_at_apogee


def create_flight_event_table(
    time,
    z,
    v_z,
    airspeed,
    a_z,
    g_force,
    Ma,
    dataset,
    liftoff_index,
    launch_rail_cleared_index,
    burnout_index,
    apogee_index,
    unit="m",
):
    """
    Create a table of parameters at key flight events.

    Args:
    - time, z, v_z, airspeed, a_z, g_force, Ma (pd.Series): Data series.
    - dataset (pd.DataFrame): The dataset containing additional flight data.
    - liftoff_index, launch_rail_cleared_index, burnout_index, apogee_index (int): Indices of key flight events.
    - unit (str): Unit of measurement for height, airspeed, etc.

    Returns:
    - pd.DataFrame: Table of parameters at key flight events.
    """
    max_g_index = g_force.idxmax()
    max_speed_Ma_index = airspeed.idxmax()
    max_q_index = dataset["q"][:apogee_index].idxmax()

    parameters_at_flight_events = pd.DataFrame(
        {
            "Time (s)": [
                round(time.iloc[liftoff_index], 2),
                round(time.iloc[launch_rail_cleared_index], 2),
                round(time.iloc[max_g_index], 2),
                round(time.iloc[max_q_index], 2),
                round(time.iloc[max_speed_Ma_index], 2),
                round(time.iloc[burnout_index], 2),
                round(time.iloc[-1], 2),
            ],
            f"Height ({unit})": [
                round(z.iloc[liftoff_index], 2),
                round(z.iloc[launch_rail_cleared_index], 2),
                round(z.iloc[max_g_index], 2),
                round(z.iloc[max_q_index], 2),
                round(z.iloc[max_speed_Ma_index], 2),
                round(z.iloc[burnout_index], 2),
                round(z.iloc[-1], 2),
            ],
            f"Vertical velocity ({unit}/s)": [
                round(v_z.iloc[liftoff_index], 2),
                round(v_z.iloc[launch_rail_cleared_index], 2),
                round(v_z.iloc[max_g_index], 2),
                round(v_z.iloc[max_q_index], 2),
                round(v_z.iloc[max_speed_Ma_index], 2),
                round(v_z.iloc[burnout_index], 2),
                round(v_z.iloc[-1], 2),
            ],
            f"Speed ({unit}/s)": [
                round(airspeed.iloc[liftoff_index], 2),
                round(airspeed.iloc[launch_rail_cleared_index], 2),
                round(airspeed.iloc[max_g_index], 2),
                round(airspeed.iloc[max_q_index], 2),
                round(airspeed.iloc[max_speed_Ma_index], 2),
                round(airspeed.iloc[burnout_index], 2),
                round(airspeed.iloc[-1], 2),
            ],
            f"Vertical accel ({unit}/s^2)": [
                round(a_z.iloc[liftoff_index], 2),
                round(a_z.iloc[launch_rail_cleared_index], 2),
                round(a_z.iloc[max_g_index], 2),
                round(a_z.iloc[max_q_index], 2),
                round(a_z.iloc[max_speed_Ma_index], 2),
                round(a_z.iloc[burnout_index], 2),
                round(a_z.iloc[-1], 2),
            ],
            f"G-force (g)": [
                round(g_force.iloc[liftoff_index], 2),
                round(g_force.iloc[launch_rail_cleared_index], 2),
                round(g_force.iloc[max_g_index], 2),
                round(g_force.iloc[max_q_index], 2),
                round(g_force.iloc[max_speed_Ma_index], 2),
                round(g_force.iloc[burnout_index], 2),
                round(g_force.iloc[-1], 2),
            ],
            f"Mach": [
                round(
                    hfunc.mach_number_fn(
                        dataset["airspeed"].iloc[liftoff_index],
                        dataset["temperature"].iloc[liftoff_index],
                    ),
                    3,
                ),
                round(
                    hfunc.mach_number_fn(
                        dataset["airspeed"].iloc[launch_rail_cleared_index],
                        dataset["temperature"].iloc[launch_rail_cleared_index],
                    ),
                    3,
                ),
                round(
                    hfunc.mach_number_fn(
                        dataset["airspeed"].iloc[max_g_index],
                        dataset["temperature"].iloc[max_g_index],
                    ),
                    3,
                ),
                round(
                    hfunc.mach_number_fn(
                        dataset["airspeed"].iloc[max_q_index],
                        dataset["temperature"].iloc[max_q_index],
                    ),
                    3,
                ),
                round(
                    hfunc.mach_number_fn(
                        dataset["airspeed"].iloc[max_speed_Ma_index],
                        dataset["temperature"].iloc[max_speed_Ma_index],
                    ),
                    3,
                ),
                round(
                    hfunc.mach_number_fn(
                        dataset["airspeed"].iloc[burnout_index],
                        dataset["temperature"].iloc[burnout_index],
                    ),
                    3,
                ),
                round(
                    hfunc.mach_number_fn(
                        dataset["airspeed"].iloc[-1], dataset["temperature"].iloc[-1]
                    ),
                    3,
                ),
            ],
            f"q (kPa)": [
                round(dataset["q"].iloc[liftoff_index] / 1000, 2),
                round(dataset["q"].iloc[launch_rail_cleared_index] / 1000, 2),
                round(dataset["q"].iloc[max_g_index] / 1000, 2),
                round(dataset["q"].iloc[max_q_index] / 1000, 2),
                round(dataset["q"].iloc[max_speed_Ma_index] / 1000, 2),
                round(dataset["q"].iloc[burnout_index] / 1000, 2),
                round(dataset["q"].iloc[-1] / 1000, 2),
            ],
        },
        index=[
            "Liftoff",
            "Off Launch Rail",
            "Max g-Force",
            "Max q",
            "Max Airspeed, Ma",
            "Burnout",
            "Apogee",
        ],
    ).sort_values(by=["Time (s)"])

    return parameters_at_flight_events
