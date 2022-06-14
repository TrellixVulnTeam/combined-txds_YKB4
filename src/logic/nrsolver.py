import numpy as np
from scipy.sparse.linalg import spsolve
from logic.matrixbuilder import MatrixBuilder
from logic.powerflowsettings import PowerFlowSettings

V_DIFF_MAX = 1
V_MAX = 2
V_MIN = -2
TX_ITERATIONS = 1000
TX_SCALE = 1.0 / TX_ITERATIONS

class NRSolver:

    def __init__(self, settings: PowerFlowSettings, network_model):
        self.settings = settings
        self.network_model = network_model

        #self.bus_mask = [False] * size_Y
        #for bus in self.buses:
        #    self.bus_mask[bus.node_Vr] = True
        #    self.bus_mask[bus.node_Vi] = True

    def solve(self, Y, J):
        return spsolve(Y, np.asarray(J, dtype=np.float64))

    def apply_limiting(self, v_next, v_previous, diff):
        #Voltage limiting
        diff_clip = np.clip(diff, -V_DIFF_MAX, V_DIFF_MAX)
        v_next_clip = np.clip(v_previous + diff_clip, V_MIN, V_MAX)

        v_next[self.bus_mask] = v_next_clip[self.bus_mask]

        return v_next

    def stamp_linear(self, Y: MatrixBuilder, J, tx_factor):
        for element in self.network_model.get_NR_invariant_elements():
            element.stamp_primal(Y, J, None, tx_factor, self.network_model)

        if self.settings.infeasibility_analysis:
            for element in self.network_model.get_NR_invariant_elements():
                element.stamp_dual(Y, J, None, tx_factor, self.network_model)

    def stamp_nonlinear(self, Y: MatrixBuilder, J, v_previous, tx_factor):
        for element in self.network_model.get_NR_variable_elements():
            element.stamp_primal(Y, J, v_previous, tx_factor, self.network_model)

        if self.settings.infeasibility_analysis:
            for element in self.network_model.get_NR_variable_elements():
                element.stamp_dual(Y, J, v_previous, tx_factor, self.network_model)

    def run_powerflow(self, v_init, tx_factor):
        v_previous = np.copy(v_init)

        Y = MatrixBuilder(self.settings)
        J_linear = [0] * len(v_init)

        self.stamp_linear(Y, J_linear, tx_factor)

        linear_index = Y.get_usage()

        for iteration_num in range(self.settings.max_iters):
            J = J_linear.copy()

            self.stamp_nonlinear(Y, J, v_previous, tx_factor)

            Y.assert_valid(check_zeros=True)

            v_next = self.solve(Y.to_matrix(), J)

            if np.isnan(v_next).any():
                raise Exception("Error solving linear system")

            diff = v_next - v_previous

            err = abs(diff)

            err_max = err.max()
            
            if err_max < self.settings.tolerance:
                return (True, v_next, iteration_num)
            elif self.settings.V_limiting and err_max > self.settings.tolerance:
                v_next = self.apply_limiting(v_next, v_previous, diff)

            v_previous = v_next
            Y.clear(retain_idx=linear_index)

        return (False, v_next, iteration_num)