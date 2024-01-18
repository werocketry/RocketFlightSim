# Import libraries, define natural constants, helper functions
import pandas as pd
import numpy as np
from configs import Prometheus, Prometheus_launch_conditions, current_airbrakes_model
import helper_functions as hfunc
import rocket_classes as rktClass
import constants as con

# Create default instances of rocket, launch conditions, airbrakes
Prometheus = rktClass.Rocket(**Prometheus)
Prometheus_launch_conditions = rktClass.LaunchConditions(**Prometheus_launch_conditions)
airbrakes_model = rktClass.Airbrakes(**current_airbrakes_model)


# Flight simulation function
def simulate_flight(
    rocket=Prometheus, launch_conditions=Prometheus_launch_conditions, timestep=0.001
):
    # Initializations
    len_characteristic = rocket.L_rocket
    A_rocket = rocket.A_rocket
    dry_mass = rocket.dry_mass
    fuel_mass_lookup = rocket.fuel_mass_lookup
    engine_thrust_lookup = rocket.engine_thrust_lookup
    Cd_rocket_at_Re = rocket.Cd_rocket_at_Re
    burnout_time = max(list(engine_thrust_lookup.keys()))

    launchpad_pressure = launch_conditions.launchpad_pressure
    launchpad_temp = launch_conditions.launchpad_temp
    L_launch_rail = launch_conditions.L_launch_rail
    launch_angle = launch_conditions.launch_angle

    time, height, speed, v_y, v_x = 0, 0, 0, 0, 0
    angle_to_vertical = np.deg2rad(90 - launch_angle)
    air_density = hfunc.air_density_fn(launchpad_pressure, launchpad_temp)
    dynamic_viscosity = hfunc.lookup_dynamic_viscosity(launchpad_temp)

    simulated_values = [
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            launchpad_temp,
            launchpad_pressure,
            air_density,
            0,
            dynamic_viscosity,
            0,
            0,
            angle_to_vertical,
        ]
    ]

    # Motor burn until liftoff
    while (
        hfunc.thrust_at_time(time, engine_thrust_lookup)
        / hfunc.mass_at_time(time, dry_mass, fuel_mass_lookup)
        <= con.F_gravity
    ):
        time += timestep
        simulated_values.append(
            [
                time,
                0,
                0,
                0,
                0,
                0,
                0,
                launchpad_temp,
                launchpad_pressure,
                air_density,
                0,
                dynamic_viscosity,
                0,
                0,
                angle_to_vertical,
            ]
        )
    liftoff_index = len(simulated_values)

    # Liftoff until launch rail cleared
    effective_L_launch_rail = L_launch_rail - rocket.h_second_lug
    while height < effective_L_launch_rail * np.cos(angle_to_vertical):
        time += timestep
        temperature = hfunc.temp_at_height(height, launchpad_temp)
        pressure = hfunc.pressure_at_height(height, launchpad_temp, launchpad_pressure)
        air_density = hfunc.air_density_fn(pressure, temperature)
        dynamic_viscosity = hfunc.lookup_dynamic_viscosity(temperature)
        reynolds_num = (air_density * speed * len_characteristic) / dynamic_viscosity
        Cd_rocket = Cd_rocket_at_Re(reynolds_num)
        q = 0.5 * air_density * (speed**2)
        F_drag = q * Cd_rocket * A_rocket
        mass = hfunc.mass_at_time(time, dry_mass, fuel_mass_lookup)
        thrust = hfunc.thrust_at_time(time, engine_thrust_lookup)
        a_y = (thrust - F_drag) * np.cos(angle_to_vertical) / mass - con.F_gravity
        a_x = (thrust - F_drag) * np.sin(angle_to_vertical) / mass
        v_y += a_y * timestep
        v_x += a_x * timestep
        speed = np.sqrt(v_y**2 + v_x**2)
        height += v_y * timestep

        simulated_values.append(
            [
                time,
                height,
                speed,
                a_y,
                a_x,
                v_y,
                v_x,
                temperature,
                pressure,
                air_density,
                q,
                dynamic_viscosity,
                reynolds_num,
                Cd_rocket,
                angle_to_vertical,
            ]
        )
    launch_rail_cleared_index = len(simulated_values)

    # Flight from launch rail cleared until burnout
    while time < burnout_time:
        time += timestep

        temperature = hfunc.temp_at_height(height, launchpad_temp)
        pressure = hfunc.pressure_at_height(height, launchpad_temp, launchpad_pressure)
        air_density = hfunc.air_density_fn(pressure, temperature)
        dynamic_viscosity = hfunc.lookup_dynamic_viscosity(temperature)
        reynolds_num = air_density * speed * len_characteristic / dynamic_viscosity
        Cd_rocket = Cd_rocket_at_Re(reynolds_num)
        q = 0.5 * air_density * (speed**2)
        F_drag = q * Cd_rocket * A_rocket
        mass = hfunc.mass_at_time(time, dry_mass, fuel_mass_lookup)
        thrust = hfunc.thrust_at_time(time, engine_thrust_lookup)
        a_y = (thrust - F_drag) * np.cos(angle_to_vertical) / mass - con.F_gravity
        a_x = (thrust - F_drag) * np.sin(angle_to_vertical) / mass
        v_y += a_y * timestep
        v_x += a_x * timestep
        speed = np.sqrt(v_y**2 + v_x**2)
        height += v_y * timestep

        angle_to_vertical = np.arctan(v_x / v_y)

        simulated_values.append(
            [
                time,
                height,
                speed,
                a_y,
                a_x,
                v_y,
                v_x,
                temperature,
                pressure,
                air_density,
                q,
                dynamic_viscosity,
                reynolds_num,
                Cd_rocket,
                angle_to_vertical,
            ]
        )
    burnout_index = len(simulated_values)

    # Flight from burnout to apogee
    previous_height = height
    mass = dry_mass
    while height >= previous_height:
        time += timestep

        temperature = hfunc.temp_at_height(height, launchpad_temp)
        pressure = hfunc.pressure_at_height(height, launchpad_temp, launchpad_pressure)
        air_density = hfunc.air_density_fn(pressure, temperature)
        dynamic_viscosity = hfunc.lookup_dynamic_viscosity(temperature)
        reynolds_num = (air_density * speed * len_characteristic) / dynamic_viscosity
        Cd_rocket = Cd_rocket_at_Re(reynolds_num)
        q = 0.5 * air_density * (speed**2)
        F_drag = q * Cd_rocket * A_rocket
        a_y = -F_drag * np.cos(angle_to_vertical) / mass - con.F_gravity
        a_x = -F_drag * np.sin(angle_to_vertical) / mass
        v_y += a_y * timestep
        v_x += a_x * timestep
        speed = np.sqrt(v_y**2 + v_x**2)
        previous_height = height
        height += v_y * timestep

        angle_to_vertical = np.arctan(v_x / v_y)

        simulated_values.append(
            [
                time,
                height,
                speed,
                a_y,
                a_x,
                v_y,
                v_x,
                temperature,
                pressure,
                air_density,
                q,
                dynamic_viscosity,
                reynolds_num,
                Cd_rocket,
                angle_to_vertical,
            ]
        )
    apogee_index = len(simulated_values)
    dataset = pd.DataFrame(
        {
            "time": [row[0] for row in simulated_values],
            "height": [row[1] for row in simulated_values],
            "speed": [row[2] for row in simulated_values],
            "a_y": [row[3] for row in simulated_values],
            "a_x": [row[4] for row in simulated_values],
            "v_y": [row[5] for row in simulated_values],
            "v_x": [row[6] for row in simulated_values],
            "temperature": [row[7] for row in simulated_values],
            "pressure": [row[8] for row in simulated_values],
            "air_density": [row[9] for row in simulated_values],
            "q": [row[10] for row in simulated_values],
            "dynamic_viscosity": [row[11] for row in simulated_values],
            "reynolds_num": [row[12] for row in simulated_values],
            "Cd_rocket": [row[13] for row in simulated_values],
            "angle_to_vertical": [row[14] for row in simulated_values],
        }
    )
    return (
        dataset,
        liftoff_index,
        launch_rail_cleared_index,
        burnout_index,
        apogee_index,
    )


# Flight with airbrakes simulation function
def simulate_airbrakes_flight(
    pre_brake_flight, rocket=Prometheus, airbrakes=airbrakes_model, timestep=0.001
):
    # Initializations
    len_characteristic = rocket.L_rocket
    A_rocket = rocket.A_rocket
    mass = rocket.dry_mass
    Cd_rocket_at_Re = rocket.Cd_rocket_at_Re

    launchpad_pressure = pre_brake_flight.pressure.iloc[0]
    launchpad_temp = pre_brake_flight.temperature.iloc[0]

    Cd_brakes = airbrakes.Cd_brakes
    max_deployment_speed = airbrakes.max_deployment_speed
    max_deployment_angle = airbrakes.max_deployment_angle
    A_brakes = airbrakes.num_flaps * airbrakes.A_flap

    pre_brake_flight["deployment_angle"] = 0

    height = pre_brake_flight["height"].iloc[-1]
    speed = pre_brake_flight["speed"].iloc[-1]
    v_y = pre_brake_flight["v_y"].iloc[-1]
    v_x = pre_brake_flight["v_x"].iloc[-1]
    time = pre_brake_flight["time"].iloc[-1]
    angle_to_vertical = np.arctan(v_x / v_y)

    deployment_angle = 0

    # for efficiency, may be removed when the simulation is made more accurate by the cd of the brakes changing during the sim:
    A_Cd_brakes = A_brakes * Cd_brakes

    simulated_values = []
    previous_height = height
    while height >= previous_height:
        time += timestep

        temperature = hfunc.temp_at_height(height, launchpad_temp)
        pressure = hfunc.pressure_at_height(height, launchpad_temp, launchpad_pressure)
        air_density = hfunc.air_density_fn(pressure, temperature)
        dynamic_viscosity = hfunc.lookup_dynamic_viscosity(temperature)
        reynolds_num = (air_density * speed * len_characteristic) / dynamic_viscosity
        Cd_rocket = Cd_rocket_at_Re(reynolds_num)
        q = 0.5 * air_density * (speed**2)

        deployment_angle = min(
            max_deployment_angle, deployment_angle + max_deployment_speed * timestep
        )

        F_drag = q * (
            np.sin(np.deg2rad(deployment_angle)) * A_Cd_brakes + A_rocket * Cd_rocket
        )
        a_y = -F_drag * np.cos(angle_to_vertical) / mass - con.F_gravity
        a_x = -F_drag * np.sin(angle_to_vertical) / mass
        v_y += a_y * timestep
        v_x += a_x * timestep
        speed = np.sqrt(v_y**2 + v_x**2)
        previous_height = height
        height += v_y * timestep

        angle_to_vertical = np.arctan(v_x / v_y)

        simulated_values.append(
            [
                time,
                height,
                speed,
                a_y,
                a_x,
                v_y,
                v_x,
                temperature,
                pressure,
                air_density,
                q,
                dynamic_viscosity,
                reynolds_num,
                Cd_rocket,
                angle_to_vertical,
                deployment_angle,
            ]
        )

    data = {
        "time": [row[0] for row in simulated_values],
        "height": [row[1] for row in simulated_values],
        "speed": [row[2] for row in simulated_values],
        "a_y": [row[3] for row in simulated_values],
        "a_x": [row[4] for row in simulated_values],
        "v_y": [row[5] for row in simulated_values],
        "v_x": [row[6] for row in simulated_values],
        "temperature": [row[7] for row in simulated_values],
        "pressure": [row[8] for row in simulated_values],
        "air_density": [row[9] for row in simulated_values],
        "q": [row[10] for row in simulated_values],
        "dynamic_viscosity": [row[11] for row in simulated_values],
        "reynolds_num": [row[12] for row in simulated_values],
        "Cd_rocket": [row[13] for row in simulated_values],
        "angle_to_vertical": [row[14] for row in simulated_values],
        "deployment_angle": [row[15] for row in simulated_values],
    }

    ascent = pd.concat([pre_brake_flight, pd.DataFrame(data)], ignore_index=True)

    return ascent

# Execution Guard
if __name__ == "__main__":
    from configs import Hyperion

    Hyperion = rktClass.Rocket(**Hyperion)

    (
        dataset,
        liftoff_index,
        launch_rail_cleared_index,
        burnout_index,
        apogee_index,
    ) = simulate_flight(rocket=Hyperion)
    ascent = simulate_airbrakes_flight(
        dataset.iloc[:burnout_index].copy(), rocket=Hyperion
    )