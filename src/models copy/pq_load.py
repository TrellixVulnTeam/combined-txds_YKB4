from collections import defaultdict


class PQLoad():

    def __init__(self):
        # The phase loads associated with this PQ load
        self.phase_loads = []
        
    def collect_Y_stamps(self, state, v):
        for phase_load in self.phase_loads:
            phase_load.collect_Y_stamps(state, v)

    def collect_J_stamps(self, state, v):
        for phase_load in self.phase_loads:
            phase_load.collect_J_stamps(state, v)

    def set_initial_voltages(self, state, v):
        for phase_load in self.phase_loads:
            phase_load.set_initial_voltages(state, v)
        
    def calculate_residuals(self, state, v):
        residual_contributions = defaultdict(lambda: 0)
        for phase_load in self.phase_loads:
            phase_load.calculate_residuals(state, v, residual_contributions)
        return residual_contributions

