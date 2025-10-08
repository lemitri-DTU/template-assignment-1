from pathlib import Path
from xml.parsers.expat import model
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import xarray as xr
# test data
T = 3  #time
p = [1.0, 2.0, 1.5]  # electricity price
g = [0.2, 0.2, 0.2]  # tariff
pv_max = [1.0, 2.0, 1.5]  # PV maximum output per hour
E_min = 2.5  # minimum energy consumption per day
# max_load = 3.0
c_pv = [1.0, 1.0, 1.0]  # PV marginal cost, assumed zero

import gurobipy as gp
from gurobipy import GRB
import numpy as np

class OptModel:
    """
    Optimization model for consumer-level flexibility (Question 1a).
    Formulae are identical to the standalone script.
    """

    def __init__(self, params):
        """
        params: dict containing
            - T: int, number of time steps
            - pv_max: list or array, PV max per hour
            - p: list or array, electricity price per hour
            - g: list or array, grid tariff per hour
            - E_min: float, minimum daily energy consumption
            - c_pv: list or array, PV marginal cost per hour
        """
        self.T = params["T"]
        self.pv_max = params["pv_max"]
        self.p = params["p"]
        self.g = params["g"]
        self.E_min = params["E_min"]
        self.c_pv = params["c_pv"]

    def solve(self):
        m = gp.Model("consumer_flex")

        # Decision variables
        I = m.addVars(self.T, lb=0, ub=10, name="Import")
        X = m.addVars(self.T, lb=0, ub=10, name="Export")
        L = m.addVars(self.T, lb=0, name="Load")
        G = m.addVars(range(self.T), lb=0, ub={t: self.pv_max[t] for t in range(self.T)}, name="PV_gen")
        C = m.addVars(self.T, lb=0, name="Curtail")

        # Constraints
        for t in range(self.T):
            m.addConstr(L[t] == (G[t] - C[t]) - X[t] + I[t], name=f"energy_balance_{t}")
            m.addConstr(G[t] <= self.pv_max[t], name=f"pv_limit_{t}")
            m.addConstr(C[t] <= G[t], name=f"curtail_limit_{t}")

        m.addConstr(gp.quicksum(L[t] for t in range(self.T)) >= self.E_min, name="min_daily_load")

        # Objective
        m.setObjective(
            gp.quicksum(
                (self.p[t] + self.g[t]) * I[t] + (self.g[t] - self.p[t]) * X[t] + self.c_pv[t] * (G[t] - C[t])
                for t in range(self.T)
            ),
            GRB.MINIMIZE
        )

        #save the attributes
        self.model = m
        self.I = I
        self.X = X
        self.L = L
        self.G = G
        self.C = C
        self.T = self.T
        self.E_min = self.E_min
        self.p = self.p

        # Solve
        m.optimize()

        # Extract results
        results = {v.varName: v.X for v in m.getVars()}
        results["Objective"] = m.ObjVal

        # Optional: print summary
        print(f"T: {self.T}, E_min: {self.E_min}")
        print("Num Vars:", m.NumVars, "Num Constrs:", m.NumConstrs)
        return results




##Version 1.0
# class OptModel:
#     """
#     Placeholder for optimization models using Gurobipy.

#     Attributes (examples):
#         N (int): Number of time steps/consumers/etc.
#         question/scenario name (str): Configuration/question identifier.
#         ...
#     """

#     def __init__(self, params):
#         self.T = params['T']
#         self.p = params['p']           # List of prices [p1, ..., pT]
#         self.g = params['g']           # List of grid tariffs [g1, ..., gT]
#         self.pv_max = params['pv_max'] # List of max PV production [pv1, ..., pvT]
#         self.c_pv = np.zeros(self.T)  # PV marginal cost (assumed zero)
#         self.E_min = params['E_min']   # Minimum daily energy consumption

#     def solve(self):
#         m = gp.Model("consumer_flex")

#         # Decision variables
#         I = m.addVars(self.T, lb=0, name="Import")
#         X = m.addVars(self.T, lb=0, name="Export")
#         G = m.addVars(self.T, lb=0, name="PV_gen")
#         L = m.addVars(self.T, lb=0, name="Load")
#         C = m.addVars(self.T, lb=0, name="Curtail")

#         print("Number of Variables:", m.NumVars)

#         # Objective
#         m.setObjective(
#             gp.quicksum((self.p[t] + self.g[t]) * I[t] + (self.g[t] - self.p[t]) * X[t] + self.c_pv[t] * (self.pv_max[t] - C[t]) for t in range(self.T)),
#             GRB.MINIMIZE
#         )

#         # Constraints
#         for t in range(self.T):
#             m.addConstr(L[t] == G[t] - X[t] + I[t], name=f"energy_balance_{t}")
#             m.addConstr(G[t] <= self.pv_max[t], name=f"pv_curtail_{t}")

#         m.addConstr(gp.quicksum(L[t] for t in range(self.T)) >= self.E_min, name="min_daily_load")
#         print("Number of constraints:", m.NumConstrs)


#         m.optimize()

#         if m.status == GRB.OPTIMAL:
#             print(f"Optimal cost: {m.ObjVal: .2f} DKK")

#         # Extract results
#         results = {
#             'Import': [I[t].X for t in range(self.T)],
#             'Export': [X[t].X for t in range(self.T)],
#             'Curtail': [G[t].X for t in range(self.T)],
#             'Load': [L[t].X for t in range(self.T)],
#             'Objective': m.ObjVal
#         }
#         return results
