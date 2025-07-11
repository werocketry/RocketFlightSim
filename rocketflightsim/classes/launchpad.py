import numpy as np

class Launchpad:
    """
    The Launchpad class is used to store the properties of a launchpad, including the launch rail/tower, hold-down clamps, and other structures that the rocket interacts with during the launch.

    Attributes
    ----------
    rail_length : float
        Length of the launch rail (m).

    rail_unit_vector_x : float
        x-component of the unit vector pointing along the launch rail.
    rail_unit_vector_y : float
        y-component of the unit vector pointing along the launch rail.
    rail_unit_vector_z : float
        z-component of the unit vector pointing along the launch rail.

    hold_down_clamp_release_time : float
        Time after ignition that the hold-down clamps release the rocket (s).
    hold_down_clamp_force : float
        Total force applied by all hold-down clamps to the rocket (N).        
    """
    def __init__(
        self,
        rail_length : float,
        launch_rail_elevation : float = 90,
        launch_rail_heading : float = 0,
        hold_down_clamp_release_time : float = 0,
        hold_down_clamp_force : float = 0
    ):
        """Initialize a Launchpad object.

        Parameters
        ----------
        rail_length : float
            Length of the launch rail (m).
        launch_rail_elevation : float, optional
            Elevation of the launch rail (deg from horizontal). Defaults to 90 (vertical launch rail).
        launch_rail_heading : float, optional
            Launch rail heading (azimuth in deg clockwise from north). 0 is north, 90 is east, 180 is south, 270 is west. Defaults to 0 (north).

        hold_down_clamp_release_time : float, optional
            Time after ignition that the hold-down clamps release the rocket (s). Defaults to 0.
        hold_down_clamp_force : float, optional
            Total force applied by all hold-down clamps to the rocket (N). Defaults to 0.
        """
        self.rail_length = rail_length

        launch_rail_heading = np.deg2rad(launch_rail_heading)
        if launch_rail_elevation == 90:
            launch_rail_elevation = 89.999999
            # TODO: find a better workaround
                # np.atan2 for compass heading?

        angle_to_vertical = np.deg2rad(90 - launch_rail_elevation)

        self.rail_unit_vector_x = np.sin(angle_to_vertical) * np.sin(launch_rail_heading)
        self.rail_unit_vector_y = np.sin(angle_to_vertical) * np.cos(launch_rail_heading)
        self.rail_unit_vector_z = np.cos(angle_to_vertical)

        self.hold_down_clamp_release_time = hold_down_clamp_release_time
        self.hold_down_clamp_force = hold_down_clamp_force