import numpy as np

class Motor:
    """
    The Motor class is used to store the properties of a rocket motor.

    Attributes
    ----------
    thrust_curve : dict
        Dictionary of thrust (N) produced by the motor at time after ignition (s).
    dry_mass : float
        Mass of the motor without fuel (kg).
    total_impulse : float
        Total impulse of the motor (Ns).
    burn_time : float
        Time it takes for the motor to burn all of its fuel (s).
    fuel_mass_curve : dict
        Dictionary of fuel mass (kg) at time after ignition (s).
    fuel_mass : float
        Total mass of fuel in the motor before ignition (kg).
    """
    # TODO add the ability to simply multiply a motor object by a scalar to get a motor object representing a cluster of that many motors?

    def __init__(
            self,
            thrust_curve : dict,
            dry_mass : float = 0,
            fuel_mass_curve : dict = None,
            fuel_mass : float = None
            ):
        """Initialize a Motor object.

        Parameters
        ----------
        thrust_curve : dict
            Dictionary of thrust (N) produced by the motor at time after ignition (s).
        dry_mass : float
            Mass of the motor without fuel (kg). Defaults to 0.
        fuel_mass_curve : dict, optional
            Dictionary of fuel mass (kg) at time after ignition (s).
        fuel_mass : float, optional
            Total mass of fuel in the motor before ignition (kg).

        Notes
        -----
        If fuel_mass_curve is not provided but fuel_mass is, fuel_mass_curve is calculated from the thrust_curve and fuel_mass, assuming fuel burn is proportional to thrust. If fuel_mass_curve is provided, fuel_mass is set to the initial mass in fuel_mass_curve. If neither are provided, fuel_mass and fuel_mass_curve are set to 0. If both are provided, fuel_mass is disregarded.
        """
        self.thrust_curve = thrust_curve
        self.dry_mass = dry_mass

        self.total_impulse = np.trapezoid(list(thrust_curve.values()), list(thrust_curve.keys()))
        # TODO: not important for this in and of itself, but for future additions, look at difference between using np.trapezoid and other integration functions
        # TODO: maybe make it only calculate total impulse if it's called on, as it slows down the sim a little
        self.burn_time = max(thrust_curve.keys())
        # TODO: add burn efficiency, some propelant mass (~2-5% ?) becomes dry mass (can just assign it to dry mass at the start of the sim/at class init)
        if fuel_mass_curve:
            self.fuel_mass_curve = fuel_mass_curve
            self.fuel_mass = fuel_mass_curve[0]
        elif fuel_mass:
            self.fuel_mass = fuel_mass
            self.fuel_mass_curve = {0: fuel_mass}
            times = list(self.thrust_curve.keys())
            for t in range(1, len(times)):
                self.fuel_mass_curve[times[t]] = self.fuel_mass_curve[times[t-1]] - (thrust_curve[times[t]] + thrust_curve[times[t-1]])/2 * (times[t] - times[t-1]) / self.total_impulse * fuel_mass
        else:
            self.fuel_mass = 0
            self.fuel_mass_curve = {
                0: 0,
                self.burn_time: 0
                }

