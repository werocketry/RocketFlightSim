import numpy as np

from . import constants as con
from . import helper_functions as hfunc

class StateVector:
    """ Needed? Just pass needed inputs into the flight function for the phase in the function that combines all the phases?

    The StateVector class is used to store the state of a rocket's flight at a given time. The state is stored as a dictionary with the following keys:

    - environment: The Environment object associated with the flight.
    - t: time (s)
    - x: displacement east (m)
    - y: displacement north (m)
    - z: altitude (m)
    - v_x: velocity east (m/s)
    - v_y: velocity north (m/s)
    - v_z: velocity vertical (m/s)
    - a_x: acceleration east (m/s^2)
    - a_y: acceleration north (m/s^2)
    - a_z: acceleration vertical (m/s^2)

    calculated values if called on:
    - angle_of_attack
    - compass_heading
    - angle_to_vertical
    - groundspeed
    - airspeed
    - total_acceleration
    - mach_number
    - dynamic_pressure
    - temperature
    - air_density
    """

    def __init__(self, environment, kinematic_tuple):
        # TODO add rocket?
        """
        """
        self.environment = environment
        self.t = kinematic_tuple[0]
        self.x = kinematic_tuple[1]
        self.y = kinematic_tuple[2]
        self.z = kinematic_tuple[3]
        self.v_x = kinematic_tuple[4]
        self.v_y = kinematic_tuple[5]
        self.v_z = kinematic_tuple[6]
        # TODO are accelerations needed? Aren't they always calculatable from the other values?
        self.a_x = kinematic_tuple[7]
        self.a_y = kinematic_tuple[8]
        self.a_z = kinematic_tuple[9]
    
    def compass_heading(self):
        """ Returns the compass heading of the rocket in degrees. """
        return hfunc.compass_heading(self.v_x, self.v_y)
    
    def angle_to_vertical(self):
        """ Returns the angle to vertical of the rocket in degrees. """
        return hfunc.angle_to_vertical(self.v_x, self.v_y, self.v_z)
    
    def groundspeed(self):
        """ Returns the groundspeed of the rocket in m/s. """
        return 1 # rename groundspeed? Does it technically only include the horizontal components?
    
    def total_acceleration(self):
        """ Returns the total acceleration of the rocket in m/s^2. """
        return np.sqrt(self.a_x**2 + self.a_y**2 + self.a_z**2)
    

class Flightpath:
    """
    The Flightpath class 
    just make it a series of StateVectors? Does it need a class in that case?
    """