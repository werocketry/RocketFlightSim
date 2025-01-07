class Parachute:
    """
    The Parachute class is used to store information about a parachute.
    
    Attributes
    ----------
    Cd : float
        The drag coefficient of the parachute.
    A : float
        The cross-sectional area of the parachute.
    deploy_altitude : float, optional
        The altitude in meters below which the parachute will deploy.
    deploy_delay : float, optional
        The time in seconds after the end of the previous flight phase to delay deployment.
    Cd_A : float
        The product of the drag coefficient and cross-sectional area of the parachute.
    
    Notes
    -----
    In RFS simulations, only one 'parachute' is simulated at a time. In practice, most people just use the main's Cd*A for descent rate calculations. In addition to providing a lot less drag than the main chute, the drogue chute is often made less efficient by being in the wake of the main chute in most recovery system designs, drastically reducing how much drag it produces. See https://www.rocketryforum.com/threads/drogue-main-chute-descent-rate.169312/post-2201266 for an illustration of what that looks like. 

    If it's desirable to simulate the effect of both parachutes while it's under main, input values for Cd and A of the main chute that give an equivalent product to the expected sum of the Cd and A contributions of both parachutes. This could mean putting in  the Cd and A of the main in one simulation and any Cd and A whose product is the sum of the main and drogue's Cd*A values, which would give bounding results. Or it could mean running advanced CFD simulations to try and find out how the wake of the main influences the drag on the drogue, and putting in values coming from that to get a good prediction of the real effects of having both parachutes deployed. For most intents and purposes, just putting in the Cd and A of the main will give more than an accurate enough simulation (and as a bonus it will give a worst-case touchdown velocity)
    """
    def __init__(self, Cd, A, deploy_altitude = None, deploy_delay = None):
        """
        Initialize a Parachute object.

        Parameters
        ----------
        Cd : float
            The drag coefficient of the parachute.
        A : float
            The cross-sectional area of the parachute.
        deploy_altitude : float, optional
            Specify to delay deployment until the rocket falls below a certain altitude in meters. Default is None.
        deploy_delay : float, optional
            Specify to delay deployment until a certain time after the end of the previous flight phase in seconds. Default is None.
        """
        self.Cd = Cd
        self.A = A
        self.Cd_A = Cd * A

        self.deploy_altitude = deploy_altitude
        self.deploy_delay = deploy_delay