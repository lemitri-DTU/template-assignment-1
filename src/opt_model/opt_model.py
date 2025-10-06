from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import xarray as xr

from data_ops import data_loader


class OptModel:
    """
    Placeholder for optimization models using Gurobipy.

    Attributes (examples):
        N (int): Number of time steps/consumers/etc.
        question/scenario name (str): Configuration/question identifier.
        ...
    """

    def __init__(self, params):
        self.T = params['T']
        self.p = params['p']           # List of prices [p1, ..., pT]
        self.g = params['g']           # List of grid tariffs [g1, ..., gT]
        self.pv_max = params['pv_max'] # List of max PV production [pv1, ..., pvT]
        self.c_pv = np.zeros(self.T)  # PV marginal cost (assumed zero)
        self.E_min = params['E_min']   # Minimum daily energy consumption

    def solve(self):
        m = gp.Model("consumer_flex")

        # Decision variables
        I = m.addVars(self.T, lb=0, name="Import")
        X = m.addVars(self.T, lb=0, name="Export")
        G = m.addVars(self.T, lb=0, name="PV_gen")
        L = m.addVars(self.T, lb=0, name="Load")

        # Objective
        m.setObjective(
            gp.quicksum((self.p[t] + self.g[t]) * I[t] + (self.g[t] - self.p[t]) * X[t] + self.c_pv[t] * G[t] for t in range(self.T)),
            GRB.MINIMIZE
        )

        # Constraints
        for t in range(self.T):
            m.addConstr(L[t] == G[t] - X[t] + I[t], name=f"energy_balance_{t}")
            m.addConstr(G[t] <= self.pv_max[t], name=f"pv_curtail_{t}")

        m.addConstr(gp.quicksum(L[t] for t in range(self.T)) >= self.E_min, name="min_daily_load")

        m.optimize()

        if m.status == GRB.OPTIMAL:
            print(f"Optimal cost: {m.ObjVal: .2f} DKK")

        # Extract results
        results = {
            'Import': [I[t].X for t in range(self.T)],
            'Export': [X[t].X for t in range(self.T)],
            'Curtail': [G[t].X for t in range(self.T)],
            'Load': [L[t].X for t in range(self.T)],
            'Objective': m.ObjVal
        }
        return results