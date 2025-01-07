class Airbrakes:
    """
    The Airbrakes class is used to store the properties of the airbrakes.

    Attributes
    ----------
    num_flaps : int
        Number of airbrake flaps.
    A_flap : float
        Cross-sectional area of each flap (m^2).
    A_brakes : float
        Total cross-sectional area of the airbrakes (m^2).
    Cd_brakes : float
        Coefficient of drag of the airbrakes.
    max_deployment_angle : float
        Maximum angle that the flaps can deploy to (deg).
    max_deployment_rate : float
        Maximum rate at which the airbrakes can be deployed (deg/s).
    max_retraction_rate : float
        Maximum rate at which the airbrakes can be retracted (deg/s).
    """

    def __init__(
        self, 
        num_flaps : int,
        A_flap : float,
        Cd_brakes : float,
        max_deployment_angle : float,
        max_deployment_rate : float,
        max_retraction_rate : float = None,
    ):
        """Initialize an Airbrakes object.

        Parameters
        ----------
        num_flaps : int
            Number of airbrake flaps.
        A_flap : float
            Cross-sectional area of each flap (m^2).
        Cd_brakes : float
            Coefficient of drag of the airbrakes.
        max_deployment_angle : float
            Maximum angle that the flaps can deploy to (deg).
        max_deployment_rate : float
            Maximum rate at which the airbrakes can be deployed (deg/s).
        max_retraction_rate : float, optional
            Maximum rate at which the airbrakes can be retracted (deg/s). Defaults to max_deployment_rate.
        """
        self.num_flaps = num_flaps
        self.A_flap = A_flap
        self.A_brakes = A_flap * num_flaps

        self.Cd_brakes = Cd_brakes

        self.max_deployment_rate = max_deployment_rate
        self.max_deployment_angle = max_deployment_angle
        if max_retraction_rate:
            self.max_retraction_rate = max_retraction_rate
        else:
            self.max_retraction_rate = max_deployment_rate
