# add both a sensitvity analysis for exploring the bounds of the expected parameter space, and a Monte Carlo analysis (separate files: extrema_sensitivity_analysis.py and monte_carlo_analysis.py). Can take most of it from airbrakes repo
    # maybe also provide a method for comparing the results of the sensitivity analysis to the results of the Monte Carlo analysis, could be interesting. Put in examples folder
# provide methods for visualizing the results of the comparison, as well as the results of each individual analysis

"""
Parameters of interest:
- from the motor class:
    - thrust curve scaled up or down providing X% more or less total impulse
    - burn time being slightly longer or shorter, reshaping the thrust curve to match
    - slight shifts in time of the points in the thrust curve?
- from the rocket class:
    - rocket mass
    - Cd_rocket_at_Ma
- from the launch conditions class:
    - launchpad pressure
    - launchpad temperature
    - launch angle
    - local T lapse rate
    - mean wind speed
    - mean wind direction
- from the Airbrakes class:
    - number of flaps
    - flap area
    - max deployment angle
    - max deployment rate
    - Cd_flap
"""