import math
import numpy as np
from anoeds.models.bus import Bus
from anoeds.global_vars import global_vars

# A toy class which models a load as a simple resistor
class ResistivePhaseLoad(Bus):

    def __init__(self, V_r, V_i, Z, phase, bus_id):
        self.bus_id = bus_id
        self.phase = phase

        self.V_r = V_r
        self.V_i = V_i
        self.Z = Z
        self.R = np.real(self.Z)
        self.X = np.imag(self.Z)
        self.G = self.R / (self.R**2 + self.X**2)
        self.B = -self.X / (self.R**2 + self.X**2)
        
    def collect_Y_stamps(self, state):
        # Indices in J of the real and imaginary voltage variables for this bus
        v_r_idx = state.bus_map[self.bus_id][0]
        v_i_idx = state.bus_map[self.bus_id][1]
        
        # Collect equations to stamp onto the Admittance matrix Y
        global_vars.add_linear_Y_stamp(state, v_r_idx, v_r_idx, self.G)
        # global_vars.add_linear_Y_stamp(state, v_r_idx, ground, -self.G)
        # global_vars.add_linear_Y_stamp(state, ground, v_r_idx, -self.G)
        # global_vars.add_linear_Y_stamp(state, ground, ground, self.G)

        global_vars.add_linear_Y_stamp(state, v_i_idx, v_i_idx, self.G)
        # global_vars.add_linear_Y_stamp(state, v_i_idx, ground, -self.G)
        # global_vars.add_linear_Y_stamp(state, ground, v_i_idx, -self.G)
        # global_vars.add_linear_Y_stamp(state, ground, ground, self.G)
        
    # def collect_J_stamps(self, state):
    #     # Do nothing
    #     pass

    def set_initial_voltages(self, state, v):
        # Indices in J of the real and imaginary voltage variables for this bus
        v_r_idx = state.bus_map[self.bus_id][0]
        v_i_idx = state.bus_map[self.bus_id][1]

        v[v_r_idx] = self.V_r
        v[v_i_idx] = self.V_i

