### `/docs`
Holds all documentation-related files.

TODO: use a site generator (MkDocs?) to make project documentation

`/docs/flight_dynamics_intro` contains an introduction to rocket flight dynamics and simulation. Other directories contain documentation for RocketFlightSim.
    - add a simplified version of RFS to the tutorials

TODO: add notes about the assumptions made in the simlator (0 AoA, dry air, wind, etc), limitations of simulators in general:
    - Total impulse a motor isn't going to be exactly the same as the motor's rating. Standard deviation of 2-3% is common. See:
        - https://www.nar.org/standards-and-testing-committee/nar-certified-motor-list/ 
        - https://www.rocketryforum.com/threads/thrust-and-impulse-variance-in-commercial-apcp-motors.172341/
        - https://www.thrustcurve.org/motors/popular.html