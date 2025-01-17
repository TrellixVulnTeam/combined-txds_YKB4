from __future__ import division
from itertools import count
import numpy as np
from sympy import symbols
from logic.lagrangesegment import LagrangeSegment
from logic.lagrangestamper import LagrangeStamper
from logic.matrixbuilder import MatrixBuilder
from models.singlephase.bus import GROUND, Bus
from models.singlephase.line import build_line_stamper_bus

#Todo: this should be unified with the capacitor class.
class Shunt:
    _ids = count(0)

    def __init__(self,
                 bus: Bus,
                 G_MW,
                 B_MVAR,
                 shunt_type,
                 Vhi,
                 Vlo,
                 Bmax,
                 Bmin,
                 Binit,
                 controlBus,
                 flag_control_shunt_bus=False,
                 Nsteps=[0],
                 Bstep=[0]):

        """ Initialize a shunt in the power grid.
        Args:
            Bus (int): the bus where the shunt is located
            G_MW (float): the active component of the shunt admittance as MW per unit voltage
            B_MVAR (float): reactive component of the shunt admittance as  MVar per unit voltage
            shunt_type (int): the shunt control mode, if switched shunt
            Vhi (float): if switched shunt, the upper voltage limit
            Vlo (float): if switched shunt, the lower voltage limit
            Bmax (float): the maximum shunt susceptance possible if it is a switched shunt
            Bmin (float): the minimum shunt susceptance possible if it is a switched shunt
            Binit (float): the initial switched shunt susceptance
            controlBus (int): the bus that the shunt controls if applicable
            flag_control_shunt_bus (bool): flag that indicates if the shunt should be controlling another bus
            Nsteps (list): the number of steps by which the switched shunt should adjust itself
            Bstep (list): the admittance increase for each step in Nstep as MVar at unity voltage
        """
        self.id = self._ids.__next__()
        self.bus = bus

        self.G = G_MW / 100
        self.B = B_MVAR / 100

    def assign_nodes(self, node_index, optimization_enabled):
        self.stamper = build_line_stamper_bus(
            self.bus, 
            GROUND, 
            optimization_enabled
            )

    def get_connections(self):
        return []

    def stamp_primal(self, Y: MatrixBuilder, J, v_previous, tx_factor, network):
        self.stamper.stamp_primal(Y, J, [self.G, self.B, tx_factor], v_previous)

    def stamp_dual(self, Y: MatrixBuilder, J, v_previous, tx_factor, network):
        self.stamper.stamp_dual(Y, J, [self.G, self.B, tx_factor], v_previous)

    def calculate_residuals(self, network, v):
        return self.stamper.calc_residuals([self.G, self.B, 0], v)
