# -*- coding: utf-8 -*-
"""
2023

@author: Bartlomiej Sarwa
"""

from devices.global_constants import SOC_min, SOC_max
import math
def ems(p_l, p_pv, SOC, p_bess, hydrogen_SOC, previous_s, ub):
    p_l = -abs(p_l)
    s = previous_s   
    net = p_l + p_pv 
    if net >= 0:
        if SOC < SOC_max and min(p_bess, (SOC_max - SOC) * ub) > net:
            s = 1 # BESS charges
        elif SOC >= SOC_max and hydrogen_SOC < 1.0:
            s = 2
        elif SOC >= SOC_max and hydrogen_SOC >= 1.0:
            s = 8
        elif SOC < SOC_max and hydrogen_SOC < 1.0:
            s = 6
        elif SOC < SOC_max and hydrogen_SOC >= 1.0:
            s = 1
    else:
        if SOC > SOC_min and min(p_bess, (SOC - SOC_min) * ub) >= abs(net):
            s = 3
        elif SOC > SOC_min and hydrogen_SOC > 0:
            s = 5
        elif SOC > SOC_min:
            s = 3
        elif SOC <= SOC_min and hydrogen_SOC <= 0:
            s = 7
        elif SOC <= SOC_min and hydrogen_SOC > 0:
            s = 4
            
    if SOC >= SOC_max and s != 2:
        SOC = SOC_max
    return s

# s = 1 - P_pv > P_l, SOC < SOC_max, p_bess > net, (SOC_max-SOC)*ub<=net - charge battery
# s = 2 - P_pv > P_l, SOC == SOC_max, hydrogen_SOC < 1.0 - produce hydrogen in SOEC
# s = 3 - P_pv < P_l, SOC > SOC_min, P_bess+P_pv > P_load  - draw power from battery
# s = 4 - P_pv < P_l, SOC == SOC_min, P_bess+P_pv < P_load - generate power in fuel cell
# s = 5 - P_pv < P_l, SOC > SOC_min, P_bess+P_pv < P_load - draw power from battery and generate power in fuel cell
# s = 6 - SOC < SOC_max and SOC_h2 < SOC_H2_max and p_bess < p_net - produce hydrogen and charge battery
# s = 7 - SOC == SOC_min and hydrogen_SOC == hydrogen_SOC_min - deficit of energy
# s = 8 - SOC == SOC_max and hydrogen_SOC == hydrogen_SOC_max - loss of energy


