# flight data from other teams to test the simulator
import sys
import os

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rocketflightsim.rocket_classes import Motor, Rocket, LaunchConditions, Airbrakes, PastFlight

""" Notre Dame Rocket Team Rocket 2020
https://github.com/RocketPy-Team/RocketPy/blob/master/docs/examples/ndrt_2020_flight_sim.ipynb
"""
Cesaroni_4895L1395_P = Motor(
    # https://www.thrustcurve.org/simfiles/5f4294d20002e90000000614/
    dry_mass = 1.958,
    thrust_curve = {
        0: 0,
        0.02: 100,
        0.04: 1400,
        0.1: 1800,
        0.2: 1500,
        0.4: 1540,
        0.8: 1591,
        1.1: 1641,
        2.4: 1481,
        2.8: 1446,
        3: 1500,
        3.18: 830,
        3.35: 100,
        3.45: 0
    },
    fuel_mass_curve = {
        0: 2.475,
        0.02: 2.47449,
        0.04: 2.46691,
        0.1: 2.41837,
        0.2: 2.33495,
        0.4: 2.18124,
        0.8: 1.86462,
        1.1: 1.6195,
        2.4: 0.593463,
        2.8: 0.297477,
        3: 0.148524,
        3.18: 0.0424968,
        3.35: 0.00252806,
        3.45: 0
    }
)
NDRT_2020_rocket = Rocket(
    # as per parameters in the GitHub
    rocket_mass = 18.998,
    motor = Cesaroni_4895L1395_P,
    A_rocket = np.pi * 0.1015 ** 2,
    Cd_rocket_at_Ma = 0.44
)
NDRT_2020_launch_conditions = LaunchConditions(
    # as per parameters in the GitHub, and using RocketPy to get launchpad pressure and temp from their weather data file (https://github.com/RocketPy-Team/RocketPy/blob/master/tests/fixtures/acceptance/NDRT_2020/ndrt_2020_weather_data_ERA5.nc)
    launchpad_pressure = 99109,
    launchpad_temp = 278.03-273.15,
    L_launch_rail = 3.353,
    launch_angle = 90,
    latitude = 41.775447,
    altitude = 206
)
NDRT_2020_flight = PastFlight(
    rocket = NDRT_2020_rocket,
    launch_conditions = NDRT_2020_launch_conditions,
    apogee = 1317,
    name="NDRT 2020"
)

""" Valetudo - Projeto Jupiter - 2019
https://github.com/RocketPy-Team/RocketPy/blob/master/docs/examples/valetudo_flight_sim.ipynb
"""
keron = Motor(
    dry_mass=0.001, # total dry mass of the rocket includes motor dry mass in the RocketPy ipynb (they put 0.001 for the motor dry mass)
    thrust_curve={
        # Thrust: https://github.com/RocketPy-Team/RocketPy/blob/master/data/motors/keron/thrustCurve.csv
        0:3.8,
        0.022:4.24,
        0.045:4.4,
        0.066:4.36,
        0.089:4.45,
        0.111:3.27,
        0.133:3.96,
        0.155:5.39,
        0.177:5.77,
        0.199:7.11,
        0.222:5.75,
        0.243:6.36,
        0.266:4.68,
        0.288:7.01,
        0.31:8.95,
        0.332:10.7,
        0.355:11.99,
        0.376:16.53,
        0.399:19.97,
        0.421:29.57,
        0.443:47.23,
        0.465:64.95,
        0.488:85.69,
        0.509:115.33,
        0.532:133.29,
        0.555:152.07,
        0.576:174.19,
        0.599:177.25,
        0.621:209.11,
        0.643:257.64,
        0.665:308.79,
        0.688:349.76,
        0.709:371.89,
        0.732:397.14,
        0.754:431.41,
        0.776:471.36,
        0.798:512.89,
        0.82:541.64,
        0.842:574.61,
        0.865:598.73,
        0.886:616.87,
        0.909:634.24,
        0.931:647.33,
        0.953:664.37,
        0.975:702.8,
        0.998:667.83,
        1.019:683.02,
        1.042:718.29,
        1.064:748.13,
        1.086:757.11,
        1.108:778.3,
        1.13:799.31,
        1.153:815.7,
        1.175:831.02,
        1.197:855.63,
        1.219:866.8,
        1.242:877,
        1.263:885.99,
        1.286:896.51,
        1.308:912.77,
        1.33:933.98,
        1.352:968.37,
        1.375:1008.08,
        1.396:1000.84,
        1.419:1007.79,
        1.441:1043.51,
        1.463:1024.67,
        1.485:1046.53,
        1.508:1068.36,
        1.529:1066.32,
        1.552:1058.33,
        1.573:1062.38,
        1.596:1065.33,
        1.618:1056.14,
        1.64:1047.75,
        1.662:1024.83,
        1.685:1003.99,
        1.707:986.5,
        1.729:962.47,
        1.751:940.92,
        1.773:922.59,
        1.796:909.34,
        1.817:869,
        1.84:867.52,
        1.862:848.35,
        1.884:829.9,
        1.906:773.38,
        1.929:751.69,
        1.95:709.27,
        1.973:988.31,
        1.994:832,
        2.017:726.36,
        2.039:615.08,
        2.061:583.97,
        2.083:538.97,
        2.106:507.19,
        2.127:484.17,
        2.15:476.66,
        2.172:459.9,
        2.194:434.45,
        2.216:409.82,
        2.238:406.57,
        2.26:392.96,
        2.283:378.46,
        2.305:356,
        2.327:318.1,
        2.35:295.23,
        2.371:274.64,
        2.394:258.5,
        2.416:252.18,
        2.438:232.4,
        2.46:209.86,
        2.483:196.54,
        2.504:185.79,
        2.527:174.41,
        2.548:159.31,
        2.571:145.07,
        2.593:132.37,
        2.615:116.62,
        2.637:101.5,
        2.659:90.1,
        2.681:82.67,
        2.704:74.9,
        2.725:71.72,
        2.748:68.25,
        2.77:66.96,
        2.792:62.71,
        2.814:60.84,
        2.837:59.91,
        2.859:58.43,
        2.881:56.31,
        2.903:56.17,
        2.925:54.23,
        2.948:52.31,
        2.969:51.41,
        2.992:51.09,
        3.014:50.19,
        3.036:48.11,
        3.058:47,
        3.081:46.79,
        3.102:44.98,
        3.125:43.66,
        3.147:43.64,
        3.169:42.73,
        3.191:40.87,
        3.213:39.45,
        3.235:38.33,
        3.258:37.66,
        3.279:36.11,
        3.302:35.99,
        3.324:34.93,
        3.346:34.76,
        3.368:33.6,
        3.391:33.06,
        3.412:31.75,
        3.435:31.79,
        3.458:32.1,
        3.479:30.96,
        3.502:30.12,
        3.523:29.68,
        3.546:30.49,
        3.568:28.77,
        3.59:28.18,
        3.612:24.73,
        3.635:24.51,
        3.656:22.38,
        3.679:23.89,
        3.701:22.29,
        3.723:22.29,
        3.745:22.54,
        3.768:22.46,
        3.789:21.23,
        3.812:22.26,
        3.833:19.41,
        3.856:19.37,
        3.878:20.65,
        3.9:18.56,
        3.922:17.91,
        3.945:18.5,
        3.966:18.61,
        3.989:14.31,
        4.012:17.72,
        4.033:16.02,
        4.056:15.73,
        4.077:17.18,
        4.1:15.02,
        4.122:11.43,
        4.144:15.18,
        4.166:14.21,
        4.188:5.26,
        4.21:7.55,
        4.233:10.93,
        4.254:8.5,
        4.277:5.74,
        4.299:10.15,
        4.321:9.34,
        4.343:10.59,
        4.366:5.36,
        4.387:8.44,
        4.41:7.13,
        4.432:10.33,
        4.454:8.18,
        4.476:9.18,
        4.498:7.54,
        4.52:8.39,
        4.543:8.33,
        4.564:6.81,
        4.587:7.39,
        4.61:7.89,
        4.631:7.21,
        4.654:6.18,
        4.676:7.66,
        4.698:6.61,
        4.72:5.05,
        4.743:5.78,
        4.764:6.51,
        4.787:5.7,
        4.808:5.93,
        4.831:6.63,
        4.853:5.8,
        4.875:5.82,
        4.897:6.33,
        4.92:5.76,
        4.941:5.18,
        4.964:6.1,
        4.986:5.96,
        5.008:5.45,
        5.03:5.8,
        5.053:6.17,
        5.074:5.9,
        5.097:5.64,
        5.118:5.91,
        5.141:5.81,
        5.164:5.53,
        5.185:5.68,
        5.208:5.94,
        5.23:5.5,
        5.252:5.68,
        5.274:5.89
    },
    fuel_mass_curve={0: 1.409}
    # fuel mass curve couldn't be found, so will make one
    # initial mass is 1.409 kg (from GitHub), final mass is 0 kg
    # total impulse is 1415.154 Ns (from GitHub)
        # verified to be the same value as taking the integral of the thrust curve
    # make the fuel burn speed proportional to the thrust
)
total_impulse = 1415.154
times = list(keron.thrust_curve.keys())
for i in range(1, len(keron.thrust_curve)):
    keron.fuel_mass_curve[times[i]] = keron.fuel_mass_curve[times[i-1]] - (keron.thrust_curve[times[i]] + keron.thrust_curve[times[i-1]])/2 * (times[i] - times[i-1]) / total_impulse * 1.409
""" # Visualization of the fuel mass curve compared to the thrust curve
# plot the fuel burn speed and the thrust on the same graph (different scales)
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots()
ax1.plot(times, [keron.thrust_curve[i] for i in keron.thrust_curve], 'b-')
ax1.set_xlabel('time (s)')
ax1.set_ylabel('Thrust (N)', color='b')
ax1.tick_params('y', colors='b')
ax2 = ax1.twinx()
ax2.plot(list(keron.fuel_mass_curve.keys()), [keron.fuel_mass_curve[i] for i in keron.fuel_mass_curve], 'r-')
ax2.set_ylabel('Fuel mass (kg)', color='r')
ax2.tick_params('y', colors='r')
plt.show()
"""
Valetudo_rocket = Rocket(
    rocket_mass=8.257,
    motor=keron,
    A_rocket=np.pi*0.04045**2,
    Cd_rocket_at_Ma = 0.9081/1.05 # TBC:
        # they define a drag coefficient of (0.9081/1.05) in the notebook, but they have a few different curves here: https://github.com/RocketPy-Team/RocketPy/tree/master/tests/fixtures/acceptance/PJ_Valetudo
        # none of them were made with CFD, so they're all probably far enough off that it's not worth the effort to spend time on it
)
Valetudo_launch_conditions = LaunchConditions(
    # as per parameters in the GitHub
    launchpad_pressure=94184,
    launchpad_temp=301.53-273.15,
    L_launch_rail=5.7,
    launch_angle=84.7,
    latitude=-23.363611,
    altitude=668
)
Valetudo_flight = PastFlight(
    rocket=Valetudo_rocket,
    launch_conditions=Valetudo_launch_conditions,
    apogee=860,
    name="Valetudo 2019"
)

""" Juno III - Projeto Jupiter 2023
https://github.com/RocketPy-Team/RocketPy/blob/master/docs/examples/juno3_flight_sim.ipynb
"""
mandioca_thrust_curve={ # per https://github.com/RocketPy-Team/RocketPy/tree/master/data/motors/mandioca
        0:8.833374233,
        0.021:11.49337423,
        0.044:15.42337423,
        0.066:19.28337423,
        0.088:26.82337423,
        0.11:44.28337423,
        0.133:86.71337423,
        0.154:164.4733742,
        0.177:228.5733742,
        0.199:264.5133742,
        0.221:313.8433742,
        0.243:366.7733742,
        0.266:436.2733742,
        0.287:495.1733742,
        0.31:552.7533742,
        0.331:616.6033742,
        0.354:693.9433742,
        0.376:756.2033742,
        0.398:822.1333742,
        0.42:873.4833742,
        0.443:932.0733742,
        0.465:967.9233742,
        0.487:1020.083374,
        0.51:1022.433374,
        0.531:1024.803374,
        0.554:1175.883374,
        0.576:1213.033374,
        0.598:1260.673374,
        0.62:1305.063374,
        0.643:1354.513374,
        0.664:1389.243374,
        0.687:1425.103374,
        0.709:1462.843374,
        0.731:1501.813374,
        0.753:1538.553374,
        0.776:1567.673374,
        0.797:1589.763374,
        0.82:1617.893374,
        0.842:1658.293374,
        0.864:1683.533374,
        0.886:1694.973374,
        0.908:1720.323374,
        0.93:1738.363374,
        0.953:1759.013374,
        0.974:1783.513374,
        0.997:1799.493374,
        1.02:1814.353374,
        1.041:1840.983374,
        1.064:1857.333374,
        1.086:1869.913374,
        1.108:1879.223374,
        1.13:1900.233374,
        1.153:1922.843374,
        1.174:1944.683374,
        1.197:1951.393374,
        1.218:1960.173374,
        1.241:1984.423374,
        1.263:1989.143374,
        1.285:2008.673374,
        1.307:2028.343374,
        1.33:2040.393374,
        1.351:2041.013374,
        1.374:2038.143374,
        1.396:2057.843374,
        1.418:2080.603374,
        1.44:2093.283374,
        1.463:2098.973374,
        1.484:2112.323374,
        1.507:2127.623374,
        1.529:2137.473374,
        1.551:2150.843374,
        1.574:2157.783374,
        1.595:2162.123374,
        1.618:2174.663374,
        1.64:2183.853374,
        1.662:2201.373374,
        1.684:2195.873374,
        1.707:2192.043374,
        1.728:2191.503374,
        1.751:2193.673374,
        1.773:2200.313374,
        1.795:2226.553374,
        1.817:2233.733374,
        1.84:2217.253374,
        1.861:2222.273374,
        1.884:2227.133374,
        1.905:2227.393374,
        1.928:2229.893374,
        1.95:2234.733374,
        1.972:2241.923374,
        1.994:2256.843374,
        2.017:2260.183374,
        2.038:2238.693374,
        2.061:2236.993374,
        2.083:2233.283374,
        2.105:2226.143374,
        2.128:2224.083374,
        2.15:2220.133374,
        2.172:2217.073374,
        2.194:2230.903374,
        2.217:2220.353374,
        2.238:2207.423374,
        2.261:2207.983374,
        2.282:2204.033374,
        2.305:2202.523374,
        2.327:2205.643374,
        2.349:2204.213374,
        2.371:2210.513374,
        2.394:2200.713374,
        2.415:2211.593374,
        2.438:2229.933374,
        2.46:2240.333374,
        2.482:2252.603374,
        2.504:2252.083374,
        2.527:2262.953374,
        2.548:2246.483374,
        2.571:2258.103374,
        2.593:2279.303374,
        2.615:2281.823374,
        2.637:2315.403374,
        2.659:2322.603374,
        2.681:2354.033374,
        2.704:2398.333374,
        2.726:2412.863374,
        2.748:2417.593374,
        2.771:2411.443374,
        2.792:2397.153374,
        2.815:2394.083374,
        2.837:2398.543374,
        2.859:2395.253374,
        2.881:2381.003374,
        2.904:2395.873374,
        2.925:2394.453374,
        2.948:2397.433374,
        2.969:2413.993374,
        2.992:2438.733374,
        3.014:2448.333374,
        3.036:2439.193374,
        3.058:2445.703374,
        3.081:2456.483374,
        3.102:2519.983374,
        3.125:2591.143374,
        3.147:2602.703374,
        3.169:2584.013374,
        3.191:2572.683374,
        3.214:2559.823374,
        3.235:2586.133374,
        3.258:2606.033374,
        3.281:2587.533374,
        3.302:2570.763374,
        3.325:2587.223374,
        3.346:2583.453374,
        3.369:2581.913374,
        3.391:2580.343374,
        3.413:2562.013374,
        3.435:2540.843374,
        3.458:2538.213374,
        3.479:2520.533374,
        3.502:2522.563374,
        3.524:2505.533374,
        3.546:2488.943374,
        3.568:2482.323374,
        3.591:2477.983374,
        3.612:2477.343374,
        3.635:2458.543374,
        3.657:2449.643374,
        3.679:2438.923374,
        3.701:2422.363374,
        3.723:2391.533374,
        3.745:2369.393374,
        3.768:2352.863374,
        3.789:2330.323374,
        3.812:2299.213374,
        3.835:2261.293374,
        3.856:2227.583374,
        3.879:2195.643374,
        3.901:2174.833374,
        3.923:2152.393374,
        3.945:2124.963374,
        3.968:2090.963374,
        3.989:2059.423374,
        4.012:2019.563374,
        4.034:1970.493374,
        4.056:1925.473374,
        4.078:1893.403374,
        4.1:1856.593374,
        4.122:1817.243374,
        4.145:1798.533374,
        4.166:1754.993374,
        4.189:1723.873374,
        4.211:1687.183374,
        4.233:1640.833374,
        4.255:1600.973374,
        4.278:1566.913374,
        4.299:1542.583374,
        4.322:1521.503374,
        4.344:1480.203374,
        4.366:1446.063374,
        4.388:1416.123374,
        4.41:1388.833374,
        4.433:1372.493374,
        4.455:1343.443374,
        4.477:1316.823374,
        4.499:1283.513374,
        4.522:1233.703374,
        4.543:1208.393374,
        4.566:1170.733374,
        4.588:1140.503374,
        4.61:1121.533374,
        4.632:1103.753374,
        4.655:1075.353374,
        4.676:1039.663374,
        4.699:1004.243374,
        4.72:959.9233742,
        4.743:932.7133742,
        4.765:904.9433742,
        4.787:882.7033742,
        4.809:855.9733742,
        4.832:824.0833742,
        4.853:794.2633742,
        4.876:768.8433742,
        4.897:731.2533742,
        4.92:702.8933742,
        4.942:685.4033742,
        4.964:652.0133742,
        4.987:625.6933742,
        5.009:597.4333742,
        5.031:571.8533742,
        5.053:548.6833742,
        5.076:518.8333742,
        5.097:500.9133742,
        5.12:479.2433742,
        5.142:458.4833742,
        5.164:437.4633742,
        5.186:418.0433742,
        5.209:394.8033742,
        5.23:371.0233742,
        5.253:348.3433742,
        5.274:328.2733742,
        5.297:290.1833742,
        5.319:277.4333742,
        5.341:255.9733742,
        5.363:232.7233742,
        5.386:215.1533742,
        5.407:198.1633742,
        5.43:179.4933742,
        5.452:173.9833742,
        5.474:155.8333742,
        5.496:140.4333742,
        5.519:123.4333742,
        5.54:97.55337423,
        5.563:78.83337423,
        5.585:64.95337423,
        5.607:51.59337423,
        5.63:34.10337423,
        5.651:21.98337423,
        5.674:10.53337423,
        5.695:-6.776625767,
        5.718:-22.18662577,
        5.74:-32.04662577,
        5.762:-40.03662577,
        5.784:-47.32662577,
        }
# reshaped as they do in the notebook to have a total impulse of 8800 Ns and a burn time of 5.8 s
def reshape_thrust_curve(thrust_curve, total_impulse, burn_time):
    time_array = np.array(list(thrust_curve.keys()))
    thrust_array = np.array(list(thrust_curve.values()))
    new_time_array = burn_time/time_array[-1] * time_array
    old_total_impulse = np.trapz(thrust_array, time_array)
    new_thrust_array = thrust_array * total_impulse / old_total_impulse
    return {new_time_array[i]: new_thrust_array[i] for i in range(len(new_time_array))}
total_impulse, burn_time = 8800, 5.8
reshaped_mandioca_thrust_curve = reshape_thrust_curve(mandioca_thrust_curve, total_impulse, burn_time)
mandioca = Motor(
    dry_mass=0.00000000001, # total dry mass of the rocket includes motor dry mass in the RocketPy ipynb (they put 0.00000000001 for the motor dry mass)
    thrust_curve=reshaped_mandioca_thrust_curve,
    fuel_mass_curve={0:8.169}
    # fuel mass curve couldn't be found, so will make one
    # initial mass is 8.169 kg (from GitHub), final mass is 0 kg
    # make the fuel burn speed proportional to the thrust
)
for i in range(1, len(mandioca.thrust_curve)):
    mandioca.fuel_mass_curve[list(mandioca.thrust_curve.keys())[i]] = mandioca.fuel_mass_curve[list(mandioca.thrust_curve.keys())[i-1]] - (mandioca.thrust_curve[list(mandioca.thrust_curve.keys())[i]] + mandioca.thrust_curve[list(mandioca.thrust_curve.keys())[i-1]])/2 * (list(mandioca.thrust_curve.keys())[i] - list(mandioca.thrust_curve.keys())[i-1]) / total_impulse * 8.169
""" # Visualization of the fuel mass curve compared to the thrust curve
# plot the fuel burn speed and the thrust on the same graph (different scales)
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots()
ax1.plot(list(mandioca.thrust_curve.keys()), [mandioca.thrust_curve[i] for i in mandioca.thrust_curve], 'b-')
ax1.set_xlabel('time (s)')
ax1.set_ylabel('Thrust (N)', color='b')
ax1.tick_params('y', colors='b')
ax2 = ax1.twinx()
ax2.plot(list(mandioca.fuel_mass_curve.keys()), [mandioca.fuel_mass_curve[i] for i in mandioca.fuel_mass_curve], 'r-')
ax2.set_ylabel('Fuel mass (kg)', color='r')
ax2.tick_params('y', colors='r')
plt.show()
"""
def Juno3_Cd_rocket_at_Ma(Ma):
    # per their curve at https://github.com/RocketPy-Team/RocketPy/tree/master/data/juno3
    # but adjusted per the following line in their notebook:
        # factor = 0.38 / juno.power_off_drag(0.6)  # From CFD analysis
    # the curve at 0.6 is 0.368, so the factor is 0.38/0.368 = 1.032609
    if Ma < 0.01: return 0.486 * 1.032609
    elif Ma < 0.02: return 0.478  * 1.032609
    elif Ma < 0.03: return 0.459 * 1.032609
    elif Ma < 0.04: return 0.443 * 1.032609
    elif Ma < 0.05: return 0.429 * 1.032609
    elif Ma < 0.06: return 0.418 * 1.032609
    elif Ma < 0.07: return 0.409 * 1.032609
    elif Ma < 0.08: return 0.401 * 1.032609
    elif Ma < 0.09: return 0.393 * 1.032609
    elif Ma < 0.10: return 0.387 * 1.032609
    elif Ma < 0.11: return 0.381 * 1.032609
    elif Ma < 0.12: return 0.376 * 1.032609
    elif Ma < 0.13: return 0.372 * 1.032609
    elif Ma < 0.14: return 0.366 * 1.032609
    elif Ma < 0.15: return 0.369 * 1.032609
    elif Ma < 0.16: return 0.37 * 1.032609
    elif Ma < 0.17: return 0.372 * 1.032609
    elif Ma < 0.18: return 0.373 * 1.032609
    elif Ma < 0.19: return 0.374 * 1.032609
    elif Ma < 0.20: return 0.374 * 1.032609
    elif Ma < 0.21: return 0.375 * 1.032609
    elif Ma < 0.22: return 0.375 * 1.032609
    elif Ma < 0.23: return 0.375 * 1.032609
    elif Ma < 0.24: return 0.375 * 1.032609
    elif Ma < 0.25: return 0.375 * 1.032609
    elif Ma < 0.26: return 0.375 * 1.032609
    elif Ma < 0.27: return 0.375 * 1.032609
    elif Ma < 0.28: return 0.375 * 1.032609
    elif Ma < 0.29: return 0.375 * 1.032609
    elif Ma < 0.30: return 0.375 * 1.032609
    elif Ma < 0.31: return 0.375 * 1.032609
    elif Ma < 0.32: return 0.375 * 1.032609
    elif Ma < 0.33: return 0.375 * 1.032609
    elif Ma < 0.34: return 0.374 * 1.032609
    elif Ma < 0.35: return 0.374 * 1.032609
    elif Ma < 0.36: return 0.374 * 1.032609
    elif Ma < 0.37: return 0.374 * 1.032609
    elif Ma < 0.38: return 0.373 * 1.032609
    elif Ma < 0.39: return 0.373 * 1.032609
    elif Ma < 0.40: return 0.373 * 1.032609
    elif Ma < 0.41: return 0.373 * 1.032609
    elif Ma < 0.42: return 0.372 * 1.032609
    elif Ma < 0.43: return 0.372 * 1.032609
    elif Ma < 0.44: return 0.372 * 1.032609
    elif Ma < 0.45: return 0.371 * 1.032609
    elif Ma < 0.46: return 0.371 * 1.032609
    elif Ma < 0.47: return 0.371 * 1.032609
    elif Ma < 0.48: return 0.371 * 1.032609
    elif Ma < 0.49: return 0.37 * 1.032609
    elif Ma < 0.50: return 0.37 * 1.032609
    elif Ma < 0.51: return 0.37 * 1.032609
    elif Ma < 0.52: return 0.37 * 1.032609
    elif Ma < 0.53: return 0.369 * 1.032609
    elif Ma < 0.54: return 0.369 * 1.032609
    elif Ma < 0.55: return 0.369 * 1.032609
    elif Ma < 0.56: return 0.369 * 1.032609
    elif Ma < 0.57: return 0.368 * 1.032609
    elif Ma < 0.58: return 0.368 * 1.032609
    elif Ma < 0.59: return 0.368 * 1.032609
    elif Ma < 0.60: return 0.368 * 1.032609
    elif Ma < 0.61: return 0.368 * 1.032609
    elif Ma < 0.62: return 0.368 * 1.032609
    elif Ma < 0.63: return 0.368 * 1.032609
    elif Ma < 0.64: return 0.368 * 1.032609
    elif Ma < 0.65: return 0.368 * 1.032609
    elif Ma < 0.66: return 0.368 * 1.032609
    elif Ma < 0.67: return 0.369 * 1.032609
    elif Ma < 0.68: return 0.369 * 1.032609
    elif Ma < 0.69: return 0.369 * 1.032609
    elif Ma < 0.70: return 0.369 * 1.032609
    elif Ma < 0.71: return 0.369 * 1.032609
    elif Ma < 0.72: return 0.369 * 1.032609
    elif Ma < 0.73: return 0.369 * 1.032609
    elif Ma < 0.74: return 0.37 * 1.032609
    elif Ma < 0.75: return 0.37 * 1.032609
    elif Ma < 0.76: return 0.37 * 1.032609
    elif Ma < 0.77: return 0.37 * 1.032609
    elif Ma < 0.78: return 0.37 * 1.032609
    elif Ma < 0.79: return 0.37 * 1.032609
    elif Ma < 0.80: return 0.371 * 1.032609
    elif Ma < 0.81: return 0.371 * 1.032609
    elif Ma < 0.82: return 0.371 * 1.032609
    elif Ma < 0.83: return 0.371 * 1.032609
    elif Ma < 0.84: return 0.371 * 1.032609
    elif Ma < 0.85: return 0.372 * 1.032609
    elif Ma < 0.86: return 0.372 * 1.032609
    elif Ma < 0.87: return 0.372 * 1.032609
    elif Ma < 0.88: return 0.372 * 1.032609
    elif Ma < 0.89: return 0.372 * 1.032609
    elif Ma < 0.90: return 0.373 * 1.032609
    elif Ma < 0.91: return 0.375 * 1.032609
    elif Ma < 0.92: return 0.383 * 1.032609
    elif Ma < 0.93: return 0.424 * 1.032609
    elif Ma < 0.94: return 0.496 * 1.032609
    elif Ma < 0.95: return 0.568 * 1.032609
    elif Ma < 0.96: return 0.64 * 1.032609
    elif Ma < 0.97: return 0.712 * 1.032609
    elif Ma < 0.98: return 0.784 * 1.032609
    elif Ma < 0.99: return 0.856 * 1.032609
    elif Ma < 1.00: return 0.928 * 1.032609
    elif Ma < 1.01: return 0.001 * 1.032609
    elif Ma < 1.02: return 0.001072 * 1.032609
    elif Ma < 1.03: return 0.001144 * 1.032609
    elif Ma < 1.04: return 0.001216 * 1.032609
    elif Ma < 1.05: return 0.001288 * 1.032609
    elif Ma < 1.06: return 0.001358 * 1.032609
    elif Ma < 1.07: return 0.001431 * 1.032609
    elif Ma < 1.08: return 0.001508 * 1.032609
    elif Ma < 1.09: return 0.001589 * 1.032609
    elif Ma < 1.10: return 0.001673 * 1.032609
    elif Ma < 1.11: return 0.001761 * 1.032609
    elif Ma < 1.12: return 0.001852 * 1.032609
    elif Ma < 1.13: return 0.001946 * 1.032609
    elif Ma < 1.14: return 0.002045 * 1.032609
    elif Ma < 1.15: return 0.002146 * 1.032609
    elif Ma < 1.16: return 0.002251 * 1.032609
    elif Ma < 1.17: return 0.002358 * 1.032609
    elif Ma < 1.18: return 0.002381 * 1.032609
    elif Ma < 1.19: return 0.002343 * 1.032609
    elif Ma < 1.20: return 0.002309 * 1.032609
    elif Ma < 1.21: return 0.002277 * 1.032609
    elif Ma < 1.22: return 0.002247 * 1.032609
    elif Ma < 1.23: return 0.00222 * 1.032609
    elif Ma < 1.24: return 0.002194 * 1.032609
    else: return 0.00217 * 1.032609
# this curve seems a bit strange, but the weird part happens after the Mach numbers the rocket will reach. Still could indicate that the curve is not that accurate
""" # plot the drag coefficient curve
import numpy as np
import matplotlib.pyplot as plt
Ma = np.linspace(0, 1.25, 100)
Cd = [Juno3_Cd_rocket_at_Ma(m) for m in Ma]
plt.plot(Ma, Cd)
plt.xlabel("Mach number")
plt.ylabel("Cd")
plt.show()
"""
Juno3_rocket = Rocket(
    rocket_mass=24.05,
    motor=mandioca,
    A_rocket=np.pi*0.0655**2,
    Cd_rocket_at_Ma=Juno3_Cd_rocket_at_Ma
)
Juno3_launch_conditions = LaunchConditions(
    # note that launchpad pressure in the GitHub notebook is 84992 Pa, but the SRAD flight computer read 86260.99854 on the ground, and the COTS flight computer read 86170 Pa. Going to stick with 84992, precision of the value makes me think it was measured with some other instrument
    launchpad_pressure=84992,
    # as per parameters in the GitHub:
    launchpad_temp=306.95-273.15,
    L_launch_rail=5.2,
    launch_angle=85,
    latitude=32.939377,
    altitude=1480
)
Juno3_flight = PastFlight(
    rocket=Juno3_rocket,
    launch_conditions=Juno3_launch_conditions,
    apogee=3213,
    name="Juno III 2023"
)

""" Bella Lui - EPFL - 2020
https://github.com/RocketPy-Team/RocketPy/blob/master/docs/examples/bella_lui_flight_sim.ipynb
"""
K828FJ = Motor(
    dry_mass=0.001, # total dry mass of the rocket includes motor dry mass in the RocketPy ipynb (they put 0.001 for the motor dry mass)
    thrust_curve={ # https://www.thrustcurve.org/simfiles/5f4294d20002e90000000442/
        0:0,
        0.01:1112.06,
        0.02:1112.06,
        0.04:1238.6,
        0.06:1303.79,
        0.08:1135.06,
        0.13:1077.54,
        0.2:1031.53,
        0.5:1016.19,
        0.65:993.18,
        1:1004.68,
        1.08:985.51,
        1.19:974.01,
        1.42:974.01,
        1.51:954.83,
        1.69:935.66,
        1.75:912.65,
        1.83:885.81,
        1.89:893.48,
        1.95:843.63,
        2:774.6,
        2.15:667.23,
        2.2:444.82,
        2.23:364.29,
        2.27:260.76,
        2.33:184.06,
        2.39:111.21,
        2.5:0
    },
    fuel_mass_curve = {
        0:1.373,
        0.01:1.36946,
        0.02:1.36238,
        0.04:1.34742,
        0.06:1.33124,
        0.08:1.31572,
        0.13:1.28051,
        0.2:1.23353,
        0.5:1.03803,
        0.65:0.942111,
        1:0.719583,
        1.08:0.668915,
        1.19:0.60032,
        1.42:0.457735,
        1.51:0.402491,
        1.69:0.294198,
        1.75:0.258906,
        1.83:0.213119,
        1.89:0.179145,
        1.95:0.145976,
        2:0.120227,
        2.15:0.0514005,
        2.2:0.0337057,
        2.23:0.0259811,
        2.27:0.0180245,
        2.33:0.00953099,
        2.39:0.00389303,
        2.5:0
    }
)
Bella_Lui_rocket = Rocket(
    rocket_mass = 18.227 - 0.001,
    motor=K828FJ,
    A_rocket=np.pi*(156/2000)**2,
    Cd_rocket_at_Ma=0.43
)
Bella_Lui_launch_conditions = LaunchConditions(
    launchpad_pressure=98043,
    launchpad_temp=286.63-273.15,
    L_launch_rail=4.2,
    launch_angle=89,
    latitude=47.213476,
    altitude=407
)
Bella_Lui_flight = PastFlight(
    rocket=Bella_Lui_rocket,
    launch_conditions=Bella_Lui_launch_conditions,
    apogee=458.97,
    name="Bella Lui 2020"
)
""" TODO: investigate why the sim performs so poorly on this flight compared to the others
This is the flight that the sim is furthest off from predicting well. Possible reasons:
- weak motor, short and quick flight leads to:
    - various small effects not accounted for in the sim made more significant
    - can't put the energy into wording it right now, but intuition
    - try simulating from burnout to apogee to see if the sim is more accurate there
    - would wind have a larger effect?
- not confident in the values the notebook provides for the motor:
    - adding on the motor mass from thrustcurve.org, the sim gives an error of -14.76, instead of +24.63
        - also lended some credence due to the sim also underestimating the other 3 flights
    - was it even the K828FJ that was used?
        - the RocketPy paper says that total impulse of the "class K solid motor" used for the flight was 2120 Ns, but the notebook says 2070.99 Ns
            - https://www.researchgate.net/publication/354034513_RocketPy_Six_Degree-of-Freedom_Rocket_Trajectory_Simulator
- using a constant Cd may not be a great approximation for a rocket hitting about Mach 0.25 
    - also, no mention of where the Cd value comes from. If it's ork or RasAero, it's likely not accurate. If it was CFD, they likely would have given a curve
- no local variation in lapse rate from the standard lapse rate accounted for. Based on how it affects a 10k launch, it can improve the accuracy by about 0.3%, which might be another small factor
Could diagnose more by comparing plots of data from the flight computer to plots from the sim, but a bit busy atm
"""

past_flights = [NDRT_2020_flight, Valetudo_flight, Juno3_flight, Bella_Lui_flight]

default_airbrakes_model = Airbrakes(
    num_flaps = 3,
    A_flap = 0.004,  # m^2  flap area
    Cd_brakes = 1,
    max_deployment_speed = 5,  # deg/s
    max_deployment_angle = 45  # deg
)

# LaunchConditions class configurations
T_lapse_rate_SA = -0.00817  # K/m
""" How T_lapse_rate at Spaceport America was determined

Only one source was found with the lapse rate for Spaceport America:
    - https://egusphere.copernicus.org/preprints/2023/egusphere-2023-633/egusphere-2023-633.pdf
    - luckily, they took their measurements in June
    - The lapse rates for the stratosphere for each of three flights were reported as follows:
        - June 1st 2021 -8.4 K/km
        - June 4th 2021 -7.9 K/km
        - June 6th 2021 -8.2 K/km
    - An average of these is what was chosen for the simulation
    - The linear lapse rate was valid for the first 10 km AGL

For future reference, it should be noted that time of year has a large effect on the lapse rate, as reported in:
    - https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-00162/article_deploy/remotesensing-14-00162.pdf?version=1640917080
    - https://hwbdocs.env.nm.gov/Los%20Alamos%20National%20Labs/TA%2004/2733.PDF
        - states that the average lapse rate in NM is:
            - -4.0F/1000ft (-7.3 K/km) in July
            - -2.5F/1000ft (-4.6 K/km) in January
        - -8.2 K/km is higher than the summer average, but generally desert areas have higher-than-normal lapse rates

The following was the most comprehensive source found for temperature lapse rates in New Mexico: 
- https://pubs.usgs.gov/bul/1964/report.pdf
- No values were found for Spaceport itself, but values for other locations in New Mexico were found
- the report says that in the western conterminous United States, temperature lapse rates are generally significantly less than the standard -6.5 K/km
- the report didn't include the date (or month) of the measurements, so I'd assume that it happened in the winter due to the low lapse rates, and/or the data being several decades old means that it's no longer as accurate due to the changing global climate
- has values for many locations in New Mexico (search for n. mex), and they ranged from -1.4 to -3.9 K/km
    - the closest station to SC was Datil, which had a lapse rate of -3.1 K/km
"""
L_launch_rail_ESRA_provided_SAC = 5.18  # m, 
""" ESRA provides teams with a 5.18m rail at competition """
launchpad_pressure_SAC = 86400  # Pa
""" How the launchpad pressure at Spaceport America was determined

- 86400 2022/06/24   WE Rocketry 2022 TeleMega/TeleMetrum data
- 86405 2022/06/23   https://github.com/ISSUIUC/flight-data/tree/master/20220623
- 86170 2023/06/21   https://github.com/ISSUIUC/flight-data/tree/master/20230621
- Truth or Consequences, NM, USA, which has an elevation 90 m lower than Spaceport America
    - 84780 http://cms.ashrae.biz/weatherdata/STATIONS/722710_s.pdf
"""
launchpad_temp_SAC = 35  # deg C
""" Ground-level temperature at Spaceport America Cup note

Flights can occur between about 07:00 and 16:30 local time, so the temperature at the time of launch can vary significantly. 35 C is about what it has been historically during the competition in mid-late June. Getting closer to launch day, it would be more accurate to use a weather forecast to get a value for expected temperature(s).

You can also consider running simulations with a range of temperatures that have been seen on launch days in the past (normally between 25 and 45 C) to see how different ground-level temperatures could affect a rocket's flight.
"""
latitude_SA = 32.99  # deg, Spaceport America's latitude
""" https://maps.app.goo.gl/rZT6MRLqHneA7wNX7 """
altitude_SA = 1401  # m, Spaceport America's elevation
""" https://www.spaceportamerica.com/faq/#toggle-id-15"""
launch_angle_SAC = 84  # deg from horizontal
"""DTEG 10.1.1: 
    > Launch vehicles will nominally launch at an elevation angle of 84° ±1°
DTEG 10.1.2:
    > Range Safety Officers reserve the right to require certain vehicles’ launch elevation be 
lower or higher if flight safety issues are identified during pre-launch activities

Teams have noted that they've been told to use angles at least as low as 80°. The Range Safety Officer picks the angle based on various factors, including the rocket being launched, the weather, and the location of the launch pad. In the design, simulation, and testing phases, use the nominal angle of 84°, but consider the possibility of the launch angle being more or less than that on competition day.
"""

Spaceport_America_avg_launch_conditions = LaunchConditions(
    launchpad_pressure = launchpad_pressure_SAC,
    launchpad_temp = launchpad_temp_SAC,
    L_launch_rail = L_launch_rail_ESRA_provided_SAC,
    launch_angle = launch_angle_SAC,
    local_T_lapse_rate = T_lapse_rate_SA,
    latitude = latitude_SA,
    altitude = altitude_SA
)