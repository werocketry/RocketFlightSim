from .motor import Motor

class Rocket:
    """
    The Rocket class is used to store the properties of a rocket.

    Attributes
    ----------
    rocket_mass : float
        Dry mass of the rocket without the motor (kg).
    motor : Motor object
        The rocket's motor.
    A_rocket : float
        Cross-sectional area of the rocket (m^2) used when Cd_rocket_at_Ma was calculated.
    Cd_rocket_at_Ma : float or function
        Coefficient of drag of the rocket. May be given as a function of Mach number or as a constant.
    h_second_rail_button : float
        Height of the second rail button (or launch lug) from the bottom of the rocket (m). This is the upper button (or launch lug) if there are only 2.
    dry_mass : float
        Total mass of the rocket without fuel (kg).
    Cd_A_rocket : function
        Coefficient of drag of the rocket multiplied by the cross-sectional area of the rocket (m^2).
    """

    def __init__(
        self,
        rocket_mass : float,
        motor : Motor,
        A_rocket : float,
        Cd_rocket_at_Ma = 0.45,
        h_second_rail_button : float = 0.8,
    ):
        """Initialize a Rocket object.

        Parameters
        ----------
        rocket_mass : float
            Dry mass of the rocket without the motor (kg).
        motor : Motor object
            The rocket's motor.
        A_rocket : float
            Cross-sectional area of the rocket (m^2). Must be the same used when the Cd_rocket_at_Ma was calculated.
        Cd_rocket_at_Ma : float or function, optional
            Coefficient of drag of the rocket. May be given as a function of Mach number or as a constant. Defaults to a constant 0.45, which is in the ballpark of what most student team competition rockets our size have.
        h_second_rail_button : float, optional
            Height of the second rail button (or launch lug) from the bottom of the rocket (m). This is the upper button (or launch lug) if there are only 2. Defaults to 0.8m, which is reasonable for most student team competition rockets. Doesn't matter much if it's not set as it changes apogee by less than 10ft on a 10k ft launch when set to 0.
        """

        self.rocket_mass = rocket_mass
        self.motor = motor
        self.A_rocket = A_rocket
        self.Cd_rocket_at_Ma = Cd_rocket_at_Ma
        self.h_second_rail_button = h_second_rail_button

        self.dry_mass = rocket_mass + motor.dry_mass
        
        if callable(Cd_rocket_at_Ma):
            def Cd_A_rocket_fn(Ma):
                return Cd_rocket_at_Ma(Ma) * A_rocket
        else:
            Cd_A_rocket = Cd_rocket_at_Ma * A_rocket
            def Cd_A_rocket_fn(Ma): return Cd_A_rocket
            # TODO: make it actually operate as a constant if it's not a function
        self.Cd_A_rocket = Cd_A_rocket_fn