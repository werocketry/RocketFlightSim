# based on https://github.com/jkb-git/Fin-Flutter-Velocity-Calculator, which took inspiration from:
    # NACA TN 4197
    # https://www.apogeerockets.com/education/downloads/Newsletter291.pdf
    # https://www.apogeerockets.com/education/downloads/Newsletter411.pdf

# TODO make another function which takes an arbitrary fin shape
    # https://github.com/jkb-git/Fin-Flutter-Velocity-Calculator/blob/main/Calculating_Fin_Flutter_Velocity_For_Complex_Fin_Shapes.pdf

import numpy as np

def flutter_velocity_trapezoidal_fins(input_dict : dict):
    # what kinds of assumptions are made in this analysis?
        # from POF 291:
            # materials are assumed to be isotropic
        # from POF 615:
            # air is an ideal gas
            # dry air
                # but humid air only gives a slight difference (0.5% in warm air), and makes the actual flutter velocity higher, so making this assumption yields a very slightly conservative flutter velocity
            # no tip to tip, which would increase flutter velocity by a factor of √2
            # trapezoidal fins

    """ Returns the flutter velocity of a trapezoidal fin.

    Ensure to use the same unit for all length inputs, and use Pa for the shear modulus and air pressure. Note that all length units cancel out except for the speed of sound's length unit, m, which is what final flutter velocity is returned as (m/s) regardless of the unit of length used for the inputs.

    Args
    ----
    - input_dict (dict): dictionary containing the following key-value pairs:
        G (float): shear modulus, Pa
        c_r (float): root chord, unit of length
        c_t (float): tip chord, unit of length
        b (float): semi-span, unit of length
        m (float): fin sweep length, unit of length
        t (float): thickness, unit of length
        P (float): pressure, Pa
        T (float): temperature, K

    Returns
    -------
    - float: flutter velocity, m/s
    """

    # Inputs
    G = input_dict['G'] # shear modulus, Pa

    c_r = input_dict['c_r'] # root chord, unit of length
    c_t = input_dict['c_t'] # tip chord, unit of length
    b = input_dict['b'] # semi-span aka height, unit of length
    m = input_dict['m'] # fin sweep length, unit of length
    t = input_dict['t'] # thickness, unit of length

    P = input_dict['P'] # pressure, Pa
    T = input_dict['T'] # temperature, K

    # Constants
    κ = 1.4 # adiabatic index aka ratio of specific heats for air, unitless

    # Calculations
    t_to_c_r = t / c_r # thickness ratio, unitless
    λ = c_t / c_r # taper ratio, unitless
    S = (c_r + c_t) * b / 2 # planform (fin) area, unit of area (unit of length squared)
    AR = b**2 / S # aspect ratio, unitless
    C_x = (2 * c_t * m + c_t ** 2 + m * c_r + c_r * c_t + c_r ** 2)/(3 * (c_t + c_r)) # location of the centroid of the fin in the axis along the fin's chord, unit of length
    ε = C_x / c_r - 0.25 # distance of the centroid behind the quarter chord, unitless

    denom_const = 24 * ε / np.pi * (λ + 1)/2 * (AR ** 3 / (t_to_c_r ** 3 * (AR + 2))) # values of the denominator inside the radical that depend on fin geometry, unitless
    fin_const = G / denom_const # values in the radical that depend on the fin (geometry and material), Pa

    a = np.sqrt(1.4 * T * 8.3144598 / 0.0289644) # speed of sound, m/s

    return a * np.sqrt(fin_const / (P * κ)) # flutter velocity, m/s

if __name__ == '__main__':
    if 1: # example in POF 615
        print(flutter_velocity_trapezoidal_fins({
            'G': 4136854000, # shear modulus, Pa = 600000 psi
            'c_r': 7.5, # root chord, in
            'c_t': 2.5, # tip chord, in
            'b': 3, # semi-span, in
            'm': 4.285, # fin sweep length, in
            't': 0.125, # thickness, in
            'P': 49633, # pressure, Pa = 7.1986 psi
            'T': 251.56 # temperature, K = -6.86 F
        }) * 3.28084) # flutter velocity, ft/s