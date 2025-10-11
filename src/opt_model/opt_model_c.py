# src/opt_model/opt_model_c.py
from pathlib import Path
import gurobipy as gp
from gurobipy import GRB
import numpy as np

class OptModelBattery:
    def __init__(self, params, Lref, alpha, battery_params=None):
        self.T = params["T"]
        self.pv_max = params["pv_max"]
        self.p = params["p"]
        self.g = params["g"]
        self.c_pv = params["c_pv"]
        self.Lref = Lref
        self.alpha = alpha

        # Battery parameters defaults
        if battery_params is None:
            battery_params = {
                "S_max":5.0, "S_min":0.0,
                "P_ch_max":2.0, "P_dis_max":2.0,
                "eta_ch":0.95, "eta_dis":0.95,
                "s0":2.5, "c_bat":0.0
            }
        self.batt = battery_params

    def solve(self, verbose=False):
        m = gp.Model("consumer_flex_battery")
        if not verbose:
            m.Params.OutputFlag = 0
        T = self.T

        # Decision variables
        I = m.addVars(T, lb=0, name="Import")
        X = m.addVars(T, lb=0, name="Export")
        L = m.addVars(T, lb=0, name="Load")
        G = m.addVars(T, lb=0, ub=self.pv_max, name="PV_gen")
        C = m.addVars(T, lb=0, name="Curtail")
        P_ch = m.addVars(T, lb=0, ub=self.batt["P_ch_max"], name="P_ch")
        P_dis = m.addVars(T, lb=0, ub=self.batt["P_dis_max"], name="P_dis")
        S = m.addVars(T+1, lb=self.batt["S_min"], ub=self.batt["S_max"], name="SoC")

        # Initial SoC
        m.addConstr(S[0] == self.batt["s0"], name="SoC_init")

        # Constraints
        for t in range(T):
            m.addConstr(L[t] == G[t] - X[t] + I[t] + P_dis[t] - P_ch[t], name=f"energy_balance_{t}")
            m.addConstr(G[t] <= self.pv_max[t], name=f"pv_limit_{t}")
            m.addConstr(C[t] <= G[t], name=f"curtail_limit_{t}")
            m.addConstr(S[t+1] == S[t] + self.batt["eta_ch"]*P_ch[t] - P_dis[t]/self.batt["eta_dis"], name=f"soc_{t}")

        # Terminal SoC constraint
        m.addConstr(S[T] >= self.batt["s0"], name="SoC_terminal")

        # Objective
        obj = gp.quicksum(
            (self.p[t] + self.g[t]) * I[t] + (self.g[t] - self.p[t]) * X[t] + self.c_pv[t] * (G[t] - C[t])
            + self.alpha * (L[t] - self.Lref[t])**2
            + self.batt["c_bat"] * (P_ch[t] + P_dis[t])
            for t in range(T)
        )
        m.setObjective(obj, GRB.MINIMIZE)
        m.optimize()

        # Extract results
        sol = {v.varName: v.X for v in m.getVars()}
        res = {
            "L": np.array([sol[f"Load[{t}]"] for t in range(T)]),
            "G": np.array([sol[f"PV_gen[{t}]"] for t in range(T)]),
            "I": np.array([sol[f"Import[{t}]"] for t in range(T)]),
            "X": np.array([sol[f"Export[{t}]"] for t in range(T)]),
            "C": np.array([sol[f"Curtail[{t}]"] for t in range(T)]),
            "P_ch": np.array([sol[f"P_ch[{t}]"] for t in range(T)]),
            "P_dis": np.array([sol[f"P_dis[{t}]"] for t in range(T)]),
            "S": np.array([sol[f"SoC[{t}]"] for t in range(T+1)]),
            "obj": m.ObjVal
        }
        return res
