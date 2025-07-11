import numpy as np

from . import helper_functions as hfunc
from . import constants as con

# Flight simulation with airbrakes - max deployment
def sim_max_airbrakes_deployment_to_apogee(rocket, environment, airbrakes, initial_state_vector, timestep = con.default_timestep):
    """
    Simulate a rocket's flight from the moment airbrake deployment begins until apogee, given the airbrakes deploy to their maximum extent as quickly as possible and remain fully deployed until apogee.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    airbrakes : Airbrakes
        An instance of the Airbrakes class.
    initial_state_vector : tuple
        A tuple detailing the state of the rocket at the time airbrake deployment begins. AAA
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, a_z, and deployment_angle of the rocket at that time.
    """
    # TODO maybe after first implementation, have it determine the exact state (between timesteps) at apogee and replace the last state with that

    # unpack environmental variables
    launchpad_temp = environment.launchpad_temp

    T_lapse_rate = environment.local_T_lapse_rate
    F_gravity = environment.local_gravity

    multiplier = environment.density_multiplier
    exponent = environment.density_exponent

    mean_wind_speed = environment.mean_wind_speed
    wind_heading = environment.wind_heading
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # unpack rocket variables
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # unpack airbrakes variables
    Cd_brakes = airbrakes.Cd_brakes
    A_brakes = airbrakes.A_brakes
    
    A_Cd_brakes = A_brakes * Cd_brakes # for efficiency. May be removed if/when the simulation is made more accurate by the Cd of the brakes changing during the sim

    max_deployment_angle = np.deg2rad(airbrakes.max_deployment_angle)
    max_deployment_rate = np.deg2rad(airbrakes.max_deployment_rate)

    # unpack simulation variables
    time = initial_state_vector[0]
    x = initial_state_vector[1]
    y = initial_state_vector[2]
    z = initial_state_vector[3]
    v_x = initial_state_vector[4]
    v_y = initial_state_vector[5]
    v_z = initial_state_vector[6]
    groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2) # will be used for AoA
    airspeed = np.sqrt((v_x - 0.2*windspeed_x)**2 + (v_y - 0.2*windspeed_y)**2 + v_z**2)

    compass_heading = np.arctan(v_x / v_y)
    angle_to_vertical = np.arccos(v_z / airspeed)

    deployment_angle = 0

    simulated_states = []

    while v_z > 0:
        # update air properties based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # calculate drag force
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        
        deployment_angle = min(max_deployment_angle, deployment_angle + max_deployment_rate * timestep)
        F_drag = q * (np.sin(deployment_angle) * A_Cd_brakes + Cd_A_rocket)

        # update rocket's motion parameters
        a_x = -F_drag * np.sin(angle_to_vertical) * np.sin(compass_heading) / mass
        a_y = -F_drag * np.sin(angle_to_vertical) * np.cos(compass_heading) / mass
        a_z = -F_drag * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        # add x and y after finishing implementation and comparing speed to old version
        x += v_x * timestep
        y += v_y * timestep
        z += v_z * timestep

        # determine new headings
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        time += timestep

        # append updated simulation values
        simulated_states.append(
            (
                time,
                x,
                y,
                z,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                deployment_angle
            )
        )

    return simulated_states

# Flight simulation with airbrakes - deployed as a function of height
def sim_airbrakes_deployment_to_apogee_fn_height(rocket, environment, airbrakes, initial_state_vector, deployment_function, timestep = con.default_timestep):
    """
    Simulate a rocket's flight from the moment airbrake deployment begins until apogee, given the airbrakes deploy according to a given deployment function.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    airbrakes : Airbrakes
        An instance of the Airbrakes class.
    initial_state_vector : tuple
        A tuple detailing the state of the rocket at the time airbrake deployment begins. AAA
    deployment_function : function
        A function that takes the height of the rocket (in meters) as an argument and returns the angle of airbrakes deployment at that height (in radians).
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, a_z, and deployment_angle of the rocket at that time.
    """
    # TODO maybe after first implementation, have it determine the exact state (between timesteps) at apogee and replace the last state with that

    # unpack environmental variables
    launchpad_temp = environment.launchpad_temp

    T_lapse_rate = environment.local_T_lapse_rate
    F_gravity = environment.local_gravity

    multiplier = environment.density_multiplier
    exponent = environment.density_exponent

    mean_wind_speed = environment.mean_wind_speed
    wind_heading = environment.wind_heading
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # unpack rocket variables
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # unpack airbrakes variables
    Cd_brakes = airbrakes.Cd_brakes
    A_brakes = airbrakes.A_brakes
    
    A_Cd_brakes = A_brakes * Cd_brakes # for efficiency. May be removed if/when the simulation is made more accurate by the Cd of the brakes changing during the sim

    # unpack simulation variables
    time = initial_state_vector[0]
    # x = initial_state_vector[1]
    # y = initial_state_vector[2]
    z = initial_state_vector[1]
    v_x = initial_state_vector[2]
    v_y = initial_state_vector[3]
    v_z = initial_state_vector[4]
    groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2) # will be used for AoA
    airspeed = np.sqrt((v_x - 0.2*windspeed_x)**2 + (v_y - 0.2*windspeed_y)**2 + v_z**2)

    compass_heading = np.arctan(v_x / v_y)
    angle_to_vertical = np.arccos(v_z / airspeed)

    simulated_states = []

    while v_z > 0:
        # update air properties based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # calculate drag force
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        
        deployment_angle = deployment_function(z)
        F_drag = q * (np.sin(deployment_angle) * A_Cd_brakes + Cd_A_rocket)

        # update rocket's motion parameters
        a_x = -F_drag * np.sin(angle_to_vertical) * np.sin(compass_heading) / mass
        a_y = -F_drag * np.sin(angle_to_vertical) * np.cos(compass_heading) / mass
        a_z = -F_drag * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        # add x and y after finishing implementation and comparing speed to old version
        # x += v_x * timestep
        # y += v_y * timestep
        z += v_z * timestep

        # determine new headings
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)

        time += timestep

        # append updated simulation values
        simulated_states.append(
            (
                time,
                # x,
                # y,
                z,
                v_x,
                v_y,
                v_z,
                a_x,
                a_y,
                a_z,
                deployment_angle
            )
        )

    return simulated_states

def sim_airbrakes_deployment_to_apogee_fn_time(rocket, environment, airbrakes, initial_state_vector, deployment_function, timestep = con.default_timestep):
    """
    Simulate a rocket's flight from the moment airbrake deployment begins until apogee, given the airbrakes deploy according to a given deployment function.

    Args
    ----
    rocket : Rocket
        An instance of the Rocket class.
    environment : Environment
        An instance of the Environment class.
    airbrakes : Airbrakes
        An instance of the Airbrakes class.
    initial_state_vector : tuple
        A tuple detailing the state of the rocket at the time airbrake deployment begins. AAA
    deployment_function : function
        A function that takes the time since airbrake deployment began (in seconds) as an argument and returns the angle of airbrakes deployment at that time (in radians).
    timestep : float, optional
        The time increment for the simulation in seconds.

    Returns
    -------
    list
        A list of tuples containing the state of the rocket at each timestep. Each tuple contains the time, x, y, z, v_x, v_y, v_z, a_x, a_y, a_z, and deployment_angle of the rocket at that time.
    """
    # TODO maybe after first implementation, have it determine the exact state (between timesteps) at apogee and replace the last state with that

    # unpack environmental variables
    launchpad_temp = environment.launchpad_temp

    T_lapse_rate = environment.local_T_lapse_rate
    F_gravity = environment.local_gravity

    multiplier = environment.density_multiplier
    exponent = environment.density_exponent

    mean_wind_speed = environment.mean_wind_speed
    wind_heading = environment.wind_heading
    windspeed_x = mean_wind_speed * np.sin(wind_heading)
    windspeed_y = mean_wind_speed * np.cos(wind_heading)

    # unpack rocket variables
    mass = rocket.dry_mass
    Cd_A_rocket_fn = rocket.Cd_A_rocket

    # unpack airbrakes variables
    Cd_brakes = airbrakes.Cd_brakes
    A_brakes = airbrakes.A_brakes
    
    A_Cd_brakes = A_brakes * Cd_brakes # for efficiency. May be removed if/when the simulation is made more accurate by the Cd of the brakes changing during the sim

    # unpack simulation variables
    time = initial_state_vector[0]
    x = initial_state_vector[1]
    y = initial_state_vector[2]
    z = initial_state_vector[3]
    v_x = initial_state_vector[4]
    v_y = initial_state_vector[5]
    v_z = initial_state_vector[6]
    groundspeed = np.sqrt(v_x**2 + v_y**2 + v_z**2) # will be used for AoA
    airspeed = np.sqrt((v_x - 0.2*windspeed_x)**2 + (v_y - 0.2*windspeed_y)**2 + v_z**2)

    compass_heading = np.arctan(v_x / v_y)
    angle_to_vertical = np.arccos(v_z / airspeed)

    simulated_states = []

    while v_z > 0:
        # update air properties based on height
        temperature = hfunc.temp_at_altitude(z, launchpad_temp, lapse_rate = T_lapse_rate)
        air_density = hfunc.air_density_optimized(temperature, multiplier, exponent)

        # calculate drag force
        Ma = hfunc.mach_number_fn(airspeed, temperature)
        Cd_A_rocket = Cd_A_rocket_fn(Ma)
        q = hfunc.calculate_dynamic_pressure(air_density, airspeed)
        
        deployment_angle = deployment_function(time)
        F_drag = q * (np.sin(deployment_angle) * A_Cd_brakes + Cd_A_rocket)

        # update rocket's motion parameters
        a_x = -F_drag * np.sin(angle_to_vertical) * np.sin(compass_heading) / mass
        a_y = -F_drag * np.sin(angle_to_vertical) * np.cos(compass_heading) / mass
        a_z = -F_drag * np.cos(angle_to_vertical) / mass - F_gravity

        v_x += a_x * timestep
        v_y += a_y * timestep
        v_z += a_z * timestep

        x += v_x * timestep
        y += v_y * timestep
        z += v_z * timestep

        # determine new headings
        airspeed = np.sqrt((v_x - windspeed_x)**2 + (v_y - windspeed_y)**2 + v_z**2)
        compass_heading = np.arctan(v_x / v_y)
        angle_to_vertical = np.arccos(v_z / airspeed)


        simulated_states.append((time, x, y, z, v_x, v_y, v_z, a_x, a_y, a_z, deployment_angle))

        time += timestep

    return simulated_states