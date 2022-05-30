from collections import defaultdict
from anoeds.global_vars import global_vars
import math

class Regulator():
    
    def __init__(self
                , phases
                , ar_step = 0.00625
                , type = "B"):
        self.regulator_phases = []
        self.phases = phases
        self.ar_step = ar_step
        self.type = type

    def collect_Y_stamps(self, state):
        for regulator in self.regulator_phases:
            v_r_f, v_i_f = state.bus_map[regulator.from_node]
            v_r_p = regulator.real_voltage_idx
            v_i_p = regulator.imag_voltage_idx
            v_r_s, v_i_s = state.bus_map[regulator.secondary_node]
            v_r_t, v_i_t = state.bus_map[regulator.to_node]

            aR = (1 + (self.ar_step * regulator.tap_position)) ** -1 if self.type == "A" else 1 - (self.ar_step * regulator.tap_position)

            # Stamps for the voltage equations for the primary coil
            global_vars.add_linear_Y_stamp(state, v_r_p, v_r_f, 1)
            global_vars.add_linear_Y_stamp(state, v_r_p, v_r_s, -aR)
            # global_vars.add_linear_Y_stamp(state, v_r_p, v_i_s, aR)
            global_vars.add_linear_Y_stamp(state, v_i_p, v_i_f, 1)
            # global_vars.add_linear_Y_stamp(state, v_i_p, v_r_s, -aR)
            global_vars.add_linear_Y_stamp(state, v_i_p, v_i_s, -aR)

            # Stamps for the new state variables (current at the voltage source)
            global_vars.add_linear_Y_stamp(state, v_r_f, v_r_p, 1)
            global_vars.add_linear_Y_stamp(state, v_i_f, v_i_p, 1)

            # Stamps for the current sources on the secondary coil (KCL)
            global_vars.add_linear_Y_stamp(state, v_r_s, v_r_p, -aR)
            # global_vars.add_linear_Y_stamp(state, v_r_s, v_i_p, -aR)
            # global_vars.add_linear_Y_stamp(state, v_i_s, v_r_p, aR)
            global_vars.add_linear_Y_stamp(state, v_i_s, v_i_p, -aR)
            
    
            # Values for the secondary coil stamps
            #r = 0#self.resistance * self.nominal_voltage ** 2  / self.rated_power
            #x = 0#self.reactance * self.nominal_voltage ** 2  / self.rated_power
            g = 1e4#r / (r**2 + x**2)
            b = 0#-x / (r**2 + x**2)

            # Stamps for the current equations for the secondary coil at the to node
            global_vars.add_linear_Y_stamp(state, v_r_t, v_r_t, g)
            global_vars.add_linear_Y_stamp(state, v_r_t, v_r_s, -g)
            global_vars.add_linear_Y_stamp(state, v_r_t, v_i_t, -b)
            global_vars.add_linear_Y_stamp(state, v_r_t, v_i_s, b)

            global_vars.add_linear_Y_stamp(state, v_i_t, v_r_t, b)
            global_vars.add_linear_Y_stamp(state, v_i_t, v_r_s, -b)
            global_vars.add_linear_Y_stamp(state, v_i_t, v_i_t, g)
            global_vars.add_linear_Y_stamp(state, v_i_t, v_i_s, -g)

            # And for the secondary node
            global_vars.add_linear_Y_stamp(state, v_r_s, v_r_t, -g)
            global_vars.add_linear_Y_stamp(state, v_r_s, v_r_s, g)
            global_vars.add_linear_Y_stamp(state, v_r_s, v_i_t, b)
            global_vars.add_linear_Y_stamp(state, v_r_s, v_i_s, -b)

            global_vars.add_linear_Y_stamp(state, v_i_s, v_r_t, -b)
            global_vars.add_linear_Y_stamp(state, v_i_s, v_r_s, b)
            global_vars.add_linear_Y_stamp(state, v_i_s, v_i_t, -g)
            global_vars.add_linear_Y_stamp(state, v_i_s, v_i_s, g)

    def calculate_residuals(self, state, v):
        residual_contributions = defaultdict(lambda: 0)
        for regulator in self.regulator_phases:
            v_r_f, v_i_f = state.bus_map[regulator.from_node]
            v_r_p = regulator.real_voltage_idx
            v_i_p = regulator.imag_voltage_idx
            v_r_s, v_i_s = state.bus_map[regulator.secondary_node]
            v_r_t, v_i_t = state.bus_map[regulator.to_node]

            aR = (1 + (self.ar_step * regulator.tap_position)) ** -1 if self.type == "A" else 1 - (self.ar_step * regulator.tap_position)

            # Stamps for the voltage equations for the primary coil
            residual_contributions[v_r_p] += v[v_r_f] * 1
            residual_contributions[v_r_p] += v[v_r_s] * -aR
            # residual_contributions[v_r_p] += v[v_i_s] * aR
            residual_contributions[v_i_p] += v[v_i_f] * 1
            # residual_contributions[v_i_p] += v[v_r_s] * -aR
            residual_contributions[v_i_p] += v[v_i_s] * -aR

            # Stamps for the new state variables (current at the voltage source)
            residual_contributions[v_r_f] += v[v_r_p] * 1
            residual_contributions[v_i_f] += v[v_i_p] * 1

            # Stamps for the current sources on the secondary coil (KCL)
            residual_contributions[v_r_s] += v[v_r_p] * -aR
            # residual_contributions[v_r_s] += v[v_i_p] * -aR
            # residual_contributions[v_i_s] += v[v_r_p] * aR
            residual_contributions[v_i_s] += v[v_i_p] * -aR
            
    
            # Values for the secondary coil stamps
            #r = 0#self.resistance * self.nominal_voltage ** 2  / self.rated_power
            #x = 0#self.reactance * self.nominal_voltage ** 2  / self.rated_power
            g = 1e4#r / (r**2 + x**2)
            b = 0#-x / (r**2 + x**2)

            # Stamps for the current equations for the secondary coil at the to node
            residual_contributions[v_r_t] += v[v_r_t] * g
            residual_contributions[v_r_t] += v[v_r_s] * -g
            residual_contributions[v_r_t] += v[v_i_t] * -b
            residual_contributions[v_r_t] += v[v_i_s] * b

            residual_contributions[v_i_t] += v[v_r_t] * b
            residual_contributions[v_i_t] += v[v_r_s] * -b
            residual_contributions[v_i_t] += v[v_i_t] * g
            residual_contributions[v_i_t] += v[v_i_s] * -g

            # And for the secondary node
            residual_contributions[v_r_s] += v[v_r_t] * -g
            residual_contributions[v_r_s] += v[v_r_s] * g
            residual_contributions[v_r_s] += v[v_i_t] * b
            residual_contributions[v_r_s] += v[v_i_s] * -b

            residual_contributions[v_i_s] += v[v_r_t] * -b
            residual_contributions[v_i_s] += v[v_r_s] * b
            residual_contributions[v_i_s] += v[v_i_t] * -g
            residual_contributions[v_i_s] += v[v_i_s] * g
        
        return residual_contributions