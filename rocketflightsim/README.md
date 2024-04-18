### `/rocketflightsim` 
This folder contains the actual Python modules and packages of the library.


#### Giorgio's Ideas
- convert these to issues. I don't want to keep comitting every time I have an idea. Also this keeps getting out of date because I have my ideas in several different places

- **Alignment of Sim Data with Experimental Data:** 
  - About 1000 ft off around motor burnout.
  - try taking data to motor burnout and simulating remainder of flight to see congruence with experimental data
    - just run sim as is and set deployment angle to 0 for the entire flight
  - this isn't a real problem; it's caused by the delay in barometric sensor data. The rocket should have been just about where the sim says it would be at motor burnout, it's just the ~1 second delay in the pressure in the rocket getting to the pressure outside the rocket that causes the discrepancy.