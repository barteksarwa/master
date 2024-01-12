import numpy as np
from .global_constants import *
import matplotlib.pyplot as plt

class SolidOxideFuelCell:
    def __init__(self, n):
        self.n_cells=n
        pass

    @staticmethod
    def partial_pressure(p, x):
        return p * x

    def equilibrium_voltage(self, t, p):
        # v_0n = (-(water_enthalpy_820 - t*water_specific_entropy_820)+(hydrogen_enthalpy_820 - t*hydrogen_specific_entropy_820)+0.5*(oxygen_enthalpy_820-t*oxygen_specific_entropy_820))/n_e/F
        v_0n = -0.0002809002*t + 1.2770578798
        # print(v_0n)
        p_h2 = self.partial_pressure(p, x_h2)*1e-5
        p_o2 = self.partial_pressure(p, x_o2)*1e-5
        p_h2o = self.partial_pressure(p, x_h2o)*1e-5
        return v_0n + R * t / n_e / F * np.log(p_h2 * p_o2 / p_h2o)

    @staticmethod
    def j_0a(t): # jednostka g_a
        return g_a * np.exp(-e_acta / R / t)  # A /m2 = A/m2* exp((J/mol / (J/(MolK)*K)))

    @staticmethod
    def j_0c(t):
        return g_c * np.exp(-e_actc / R / t) # A /m2 = A/m2* exp((J/mol / (J/(MolK)*K)))

    def v_acta(self, t, j):
        return R * t * np.arcsinh(j / 2 / self.j_0a(t)) / n_e / F # V 

    def v_actc(self, t, j):
        return R * t * np.arcsinh(j / 2 / self.j_0c(t)) / n_e / F # V

    @staticmethod
    def v_ohm(t, j):
        return j * (a_a * sigma_a * np.exp(b_a / t) + a_c *
                  sigma_c * np.exp(b_c / t) + a_e * sigma_e * np.exp(b_e / t)) #V

    @staticmethod
    def binary_diffusion_coefficient_anode_h2o(t, p):
        p_fuller = p*1e-5 #bar
        m_h2o_h2_fuller = m_h2o_h2*1000 #g/mol
        D_fuller = 0.00143 * t**1.75 / (p_fuller * np.sqrt(m_h2o_h2_fuller) * \
                                ((sigma_f_h2o)**1/3 + (sigma_f_h2)**1/3)**2) #cm2/s
        return D_fuller*1e-4 #m2/s
            
    @staticmethod
    def binary_diffusion_coefficient_anode_h2(t, p):
        p_fuller = p*1e-5 #bar
        m_h2o_h2_fuller = m_h2o_h2*1000 #g/mol
        D_fuller = 0.00143 * t**1.75 / (p_fuller * np.sqrt(m_h2o_h2) * \
                                ((sigma_f_h2o)**1/3 + (sigma_f_h2)**1/3)**2)
        return D_fuller*1e-4 #m2/sr

    def binary_diffusion_coefficient_cath(self, t, p):
        p_fuller = p*1e-5 #bar
        m_n2_o2_fuller = m_n2_o2*1000 #g/mol
        D_fuller = 0.00143 * t**1.75 / (p_fuller * np.sqrt(m_n2_o2) *
                                ((sigma_f_o2)**1/3 + (sigma_f_n2)**1/3)**2)
        return D_fuller * 1e-4 #m2/s

    @staticmethod
    def knudsen_h2o(t): # m2/s
        return 4 / 3 * r_pore * np.sqrt(8 * R * t / np.pi / m_h2o) # r_pore =[m], R =[ J/mol K], T = [K], m_h2o = [kg/mol]

    @staticmethod
    def knudsen_o2(t): # m2/s
        return 4 / 3 * r_pore * np.sqrt(8 * R * t / np.pi / m_o2) # r_pore =[m], R =[ J/mol K], T = [K], m_h2o = [kg/mol]
    
    @staticmethod
    def knudsen_h2(t): # m2/s
        return 4 / 3 * r_pore * np.sqrt(8 * R * t / np.pi / m_h2) # r_pore =[m], R =[ J/mol K], T = [K], m_h2o = [kg/mol]

    def eff_diff_steam(self, t, p):
        return electrode_porosity / electrode_tortuosity / \
            (1 / self.knudsen_h2o(t) + 1 / 
             self.binary_diffusion_coefficient_anode_h2o(t, p)) #m2/s

    def eff_diff_oxygen(self, t, p):
        return electrode_porosity / electrode_tortuosity / \
            (1 / self.knudsen_o2(t) + 1 / self.binary_diffusion_coefficient_cath(t, p)) #m2/s

    def eff_diff_hydrogen(self, t, p):
        return electrode_porosity / electrode_tortuosity / \
            (1 / self.knudsen_h2(t) + 1 / self.binary_diffusion_coefficient_cath(t, p)) #m2/s

    def v_conca(self, t, j, p):
        p_h2o = self.partial_pressure(p, x_h2o)
        p_h2 = self.partial_pressure(p, x_h2)   
        return - R * t / n_e / F * np.log\
            ((1 - j * R * t * sigma_a / 2 / F / self.eff_diff_hydrogen(t, p) / p_h2)/
            (1 + j * R * t * sigma_a / 2 / F / self.eff_diff_hydrogen(t, p) / p_h2o)) 
# sprawdzic jednostke D_eff, powinno być w tym miejscu D_eff = [m2/s] J = [A/m2], R =[ J/mol K] T = [K] F =[C/mol] sigma = [m] p = [Pa]

            
    def v_concc(self, t, j, p):
        p_o2 = self.partial_pressure(p, x_o2)
        return R * t / n_e / F * np.log((1 + j * R * t * sigma_a /
                2 / F / self.eff_diff_oxygen(t, p) / p_o2)**.5)


    def first_principle_model(self, t, j, p):
        j0a = self.j_0a(t)
        j0c = self.j_0c(t)
        p_h2 = self.partial_pressure(p, x_h2)
        p_o2 = self.partial_pressure(p, x_o2)
        p_h2o = self.partial_pressure(p, x_h2o)
        v_n = self.equilibrium_voltage(t, p)
        eta_act_ano = self.v_acta(t, j)
        eta_act_cat = self.v_actc(t, j)
        eta_ohm =  self.v_ohm(t, j)
        eta_con_ano = self.v_conca(t, j, p)
        eta_con_cat = self.v_concc(t, j,p)
        v_c = v_n - eta_act_ano -eta_act_cat - eta_ohm -\
            eta_con_ano - eta_con_cat
        return v_c

    # def collision_integral(t):
    #     t_ih2 = t/t_refh2

    # @staticmethod
    # def p_sofc(v_c, j, w_sc):
    #     return v_c * j * a_cell * n_cells + w_sc

    @staticmethod
    def w_sc(s):
        if s in range(3, 6, 1):
            return 1
        else:
            return 0

    def w_sofc(self, t, j, p):
        #print('xxx', j)
        return self.first_principle_model(t, j, p) \
            * j * a_cell * self.n_cells

    def w_sofc_diff(self, t, j, p, w_0):
        return w_0 - self.w_sofc(t, j, p)

    def s_gen(self, t, j):
        v_conc = self.v_conca(t, j, p) + self.v_concc(t, j, p)
        v_act = self.v_acta(t, j) + self.v_actc(t, j)
        return n_e * F * (v_act + self.v_ohm(t, j) + v_conc) / t
    
    def q_sofc(self, t, s_gen, s_in, s_out):
        return -t * self.s_gen(t, j) - t * (s_in - s_out)

    def e_th_sofc(self, t, q_soec):
        return self.q_sofc(t, s_gen, s_in, s_out) * (1 - t_0 / t)

    @staticmethod
    def central_difference_quotient(f, t, j, p, w_0, h=1e-6):
        return (f(t, j + h, p ,w_0) \
                - f(t, j - h, p, w_0)) / (2 * h)

    def newton_method(self, f, t, j, p, w_0, epsilon=1e-12, max_iter=200):
        for i in range(max_iter):
            wj = f(t, j, p, w_0)
            #print(wj)
            if abs(wj) < epsilon:
                return j
            dwj = self.central_difference_quotient(f, t, j, p, w_0)
            #print(dwj)
            # if abs(dwj) < 1e-6:
                # return j
            j = j - wj / dwj
            #print(j)
            #input()
            if j < 0:
                j = 0
        return j


    def hydrogen_consumption_rate(self,j):
        i = j * a_cell * self.n_cells
        return i * coulomb / avogadro_number / 2
    
    def plot_fuel_cell_characteristic(self):
        i0 = np.linspace(0, 15000, 10000)
        v = []
        p = []
        for i in i0:
            v.append(self.first_principle_model(t, i, 115000))

        for i, k in zip(i0, v):
            p.append(i * k)

        max_p = np.nanmax(p)
        index_max_j = np.nanargmax(p)
        max_j = i0[index_max_j]
        print(f'Maximum power of fuel cell {max_p}')
        max_index = np.nanargmax(p)

        plt.plot(i0, p, '-b', markersize=5)
        # plt.plot(i[max_index], max_p, 'bo', markersize=8)
        plt.xlabel("j (A/m2)")
        plt.ylabel("p (W/m2)")
        plt.title('Fuel cell characteristic')
        plt.show()
        return max_p, max_j

if __name__== "__main__":
    i = 7000 #A/m2
    p = 115000 #Pa
    t = 1173 #Kelvin
    n_cells=8
    sofc_dev = SolidOxideFuelCell(n_cells)
    print(sofc_dev.eff_diff_hydrogen(t,p))
    print(f'Nernst voltage of SOFC {sofc_dev.equilibrium_voltage(t, p)}')
    print(f'Activation losses SOFC anode {sofc_dev.v_acta(t, i)}')
    print(f'Activation losses SOFC cathode {sofc_dev.v_actc(t, i)}')
    print(f'Concentration losses SOFC anode {sofc_dev.v_conca(t, i, p)}')
    print(f'Ohmic losses SOFC {sofc_dev.v_ohm(t, i)}')
    print(f'SOFC voltage {sofc_dev.first_principle_model(t, i, p)}')
    j = np.linspace(0,12000,1000)
    
    plt.plot(j,sofc_dev.w_sofc(t,j,115000) )
    # plt.show()
    # plt.show()
    print(sofc_dev.newton_method(sofc_dev.w_sofc_diff, t, 8349.38493849385, 115000, 390.8569212126979))
    
    # p_max_fc, j_max =  sofc_dev.plot_fuel_cell_characteristic()
    # print(p_max_fc * n_cells * a_cell, j_max)

