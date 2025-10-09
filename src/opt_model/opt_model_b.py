# src/opt_model/opt_model_b.py
import gurobipy as gp
from gurobipy import GRB
import numpy as np

class OptModelFlex:
    """
    Consumer-level flexibility model for Question 1.(b).

    Minimizes: sum_t [ (p_t+g_t) I_t + (g_t - p_t) X_t + c_pv_t * G_t + alpha * (L_t - Lref_t)^2 ]
    Subject to:
        L_t = G_t - X_t + I_t
        0 <= G_t <= pv_max_t
        0 <= L_t <= Lmax_t
        I_t, X_t >= 0
    """

    def __init__(self, params, Lref=None, alpha=1.0):
        """
        params: dict with keys 'T', 'pv_max', 'p', 'g', 'c_pv', optionally 'L_max' or 'max_load'
        Lref: array-like of length T (reference/preferred hourly load). If None -> uniform or zeros.
        alpha: discomfort weight (float); multiplies squared deviation term.
        """
        self.T = int(params["T"])
        self.pv_max = np.array(params["pv_max"], dtype=float)
        self.p = np.array(params["p"], dtype=float)
        self.g = np.array(params["g"], dtype=float)
        self.c_pv = np.array(params.get("c_pv", np.zeros(self.T)), dtype=float)
        # load upper bound: if provided in params, use it; otherwise large default
        if "L_max" in params:
            self.L_max = np.array(params["L_max"], dtype=float)
        elif "max_load" in params:
            self.L_max = np.full(self.T, float(params["max_load"]))
        else:
            self.L_max = np.full(self.T, 1e6)  # effectively unbounded

        # Lref
        if Lref is None:
            # default: use zeros (consumer prefers zero) or uniform small if you prefer
            self.Lref = np.zeros(self.T)
        else:
            self.Lref = np.array(Lref, dtype=float)

        self.alpha = float(alpha)

        # placeholders for model and variables
        self.model = None
        self.I = None; self.X = None; self.G = None; self.L = None

    def build_model(self):
        m = gp.Model("consumer_flex_b")
        # create variables
        self.I = m.addVars(self.T, lb=0.0, name="Import")
        self.X = m.addVars(self.T, lb=0.0, name="Export")
        # Load with upper bound
        self.L = m.addVars(self.T, lb=0.0, ub={t: self.L_max[t] for t in range(self.T)}, name="Load")
        # PV generation with per-hour ub
        self.G = m.addVars(self.T, lb=0.0, ub={t: self.pv_max[t] for t in range(self.T)}, name="PV_gen")

        # constraints
        for t in range(self.T):
            m.addConstr(self.L[t] == self.G[t] - self.X[t] + self.I[t], name=f"energy_balance_{t}")

        # objective: linear terms + quadratic discomfort
        linear = gp.quicksum((self.p[t] + self.g[t]) * self.I[t] + (self.g[t] - self.p[t]) * self.X[t] + self.c_pv[t] * self.G[t]
                             for t in range(self.T))
        # quadratic term: alpha * sum_t (L_t - Lref_t)^2
        # build quadratic expression
        quad = gp.QuadExpr()
        for t in range(self.T):
            # (L - Lref)^2 = L^2 - 2 Lref L + Lref^2 (constant term Lref^2 can be dropped from optimization)
            quad.add(self.L[t] * self.L[t], 1.0)       # coefficient for L^2
            # add linear part from quadratic: -2 * Lref * L
            if self.Lref[t] != 0:
                linear += (-2.0 * self.alpha * self.Lref[t]) * self.L[t]
        # Note: we add alpha * (L^2) separately because gp.setObjective accepts QuadExpr
        # Weighted quadratic: alpha * sum L^2 + (already added linear part above)
        quad *= self.alpha

        # set objective
        m.setObjective(linear + quad, GRB.MINIMIZE)

        # store model
        self.model = m

    def solve(self, verbose=False):
        if self.model is None:
            self.build_model()
        if not verbose:
            self.model.Params.OutputFlag = 0
        self.model.optimize()

        # save solution values on object for easy access
        sol = {}
        if self.model.status == GRB.OPTIMAL or self.model.status == GRB.SUBOPTIMAL:
            sol["I"] = np.array([self.I[t].X for t in range(self.T)])
            sol["X"] = np.array([self.X[t].X for t in range(self.T)])
            sol["G"] = np.array([self.G[t].X for t in range(self.T)])
            sol["L"] = np.array([self.L[t].X for t in range(self.T)])
            sol["obj"] = self.model.ObjVal
        else:
            sol["I"] = sol["X"] = sol["G"] = sol["L"] = np.zeros(self.T)
            sol["obj"] = None

        # also keep references for analysis
        self.solution = sol
        return sol

    def get_duals(self):
        """
        Return dict of relevant duals (shadow prices):
          - lambda_t: energy balance multipliers
          - (no explicit dual for L bounds unless asked)
        """
        if self.model is None:
            raise RuntimeError("Model not built/solved yet.")
        lambda_t = np.array([self.model.getConstrByName(f"energy_balance_{t}").Pi for t in range(self.T)])
        # If you want load bounds duals:
        load_lower_duals = np.array([self.model.getConstrByName(f"Load[{t}]_lb") is None for t in range(self.T)])  # placeholder
        return {"lambda_t": lambda_t}
