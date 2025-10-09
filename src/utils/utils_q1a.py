"placeholder for various utils functions"

import json
import csv
import pandas as pd
from pathlib import Path

# example function to load data from a specified directory
def load_dataset(question_name):
    base_path = Path("../data") / question_name
    result = {}
 
    for file_path in base_path.glob("*"):
        stem = file_path.stem
        suffix = file_path.suffix.lower()
 
        try:
            if suffix == '.json':
                with open(file_path, 'r') as f:
                    result[stem] = json.load(f)
            elif suffix == '.csv':
                with open(file_path, 'r') as f:
                    result[stem] = list(csv.DictReader(f))
            else:
                with open(file_path, 'r') as f:
                    result[stem] = f.read()
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
 
    return result

# example function to save model results in a specified directory
def save_model_results():
    """Placeholder for save_model_results function."""
    pass

# example function to plot data from a specified directory
def plot_data():
    """Placeholder for plot_data function."""
    pass

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

#analysis scenarios for question 1a-v
import numpy as np
import matplotlib.pyplot as plt
from data_ops.data_loader import DataLoader
from opt_model.opt_model import OptModel
import os
import pandas as pd

OUTPUT_DIR = "src/output/question1a"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# 1) read data and create base params
loader = DataLoader("data")           # DataPath
loader.load_question1a()
base_params = loader.get_params_for_q1a()  # dict with T, pv_max, p, g, E_min, c_pv

T = int(base_params["T"])
pv_max = np.array(base_params["pv_max"])

# Helper: build a params modifiable copy
def copy_params(base):
    return {
        "T": int(base["T"]),
        "pv_max": np.array(base["pv_max"]),
        "p": np.array(base["p"]),
        "g": np.array(base["g"]),
        "E_min": float(base["E_min"]),
        "c_pv": np.array(base["c_pv"])
    }

# If DataLoader's p/g/c_pv are placeholders, create base p/g here:
base = copy_params(base_params)
# ensure p/g/c_pv exist (if not, assign placeholders)
if np.all(base["p"] == 0) or len(base["p"]) != T:
    base["p"] = np.linspace(1.0, 3.0, T)
if len(base["g"]) != T:
    base["g"] = np.full(T, 0.2)
if len(base["c_pv"]) != T:
    base["c_pv"] = np.zeros(T)

# 2) Define scenarios as small functions returning params dict
def scenario_base():
    return copy_params(base)

def scenario_flat_price():
    p = np.full(T, np.mean(base["p"]))
    params = copy_params(base)
    params["p"] = p
    return params

def scenario_high_tariff():
    params = copy_params(base)
    params["g"] = np.full(T, 1.0)   # big grid fee
    return params

def scenario_price_spike():
    params = copy_params(base)
    p = np.array(base["p"]).copy()
    spike_hour = min(12, T-1)
    p[spike_hour] = p.max() * 5.0   # big spike at hour 12 (or last hour if T small)
    params["p"] = p
    return params

def scenario_low_export_price():
    params = copy_params(base)
    # make p small so p < g for many hours
    params["p"] = np.full(T, 0.05)
    params["g"] = np.full(T, 0.2)
    return params

def scenario_high_pv_cost():
    params = copy_params(base)
    params["c_pv"] = np.full(T, 2.0)  # PV expensive per kWh
    return params

scenarios = {
    "base": scenario_base,
    "flat_price": scenario_flat_price,
    "high_tariff": scenario_high_tariff,
    "price_spike": scenario_price_spike,
    "low_export": scenario_low_export_price,
    "pv_high_cost": scenario_high_pv_cost
}

# 3) Metrics to compute from the solution
def compute_metrics(opt: OptModel):
    """
    Assumes opt.solve() has been called and opt.model is the gurobi model.
    Returns: dict of time series (Import, Export, PV_gen, Curtail, Load),
             scalar metrics (net_cost, profit, self_consumption_ratio, exported_energy).
    """
    # get solution arrays
    T = opt.T
    m = opt.model
    I = np.array([opt.I[t].X for t in range(T)])
    X = np.array([opt.X[t].X for t in range(T)])
    G = np.array([opt.G[t].X for t in range(T)])
    C = np.array([opt.C[t].X for t in range(T)])
    L = np.array([opt.L[t].X for t in range(T)])

    # metrics
    net_cost = np.sum((opt.p + opt.g) * I + (opt.g - opt.p) * X + opt.c_pv * (G - C))
    profit = -net_cost   # if negative cost => profit positive
    total_pv_generated = G.sum()
    total_pv_self_consumed = np.maximum(G - C - X, 0).sum()   # PV used on-site
    self_consumption_ratio = total_pv_self_consumed / total_pv_generated if total_pv_generated > 0 else np.nan

    exported = X.sum()
    imported = I.sum()

    # shadow prices: energy balance duals (lambda_t) and min_daily_load dual
    lambda_t = np.array([m.getConstrByName(f"energy_balance_{t}").Pi for t in range(T)])
    alpha = m.getConstrByName("min_daily_load").Pi

    metrics = {
        "I": I, "X": X, "G": G, "C": C, "L": L,
        "net_cost": float(net_cost),
        "profit": float(profit),
        "total_pv_generated": float(total_pv_generated),
        "total_pv_self_consumed": float(total_pv_self_consumed),
        "self_consumption_ratio": float(self_consumption_ratio),
        "exported": float(exported),
        "imported": float(imported),
        "lambda_t": lambda_t,
        "alpha": float(alpha)
    }
    return metrics

# 4) run all scenarios and collect results
results_summary = {}
for name, scen_fn in scenarios.items():
    params = scen_fn()
    model = OptModel(params)   # instantiate
    res = model.solve()        # solve; model.model, variables saved inside
    metrics = compute_metrics(model)
    results_summary[name] = metrics
    print(f"Scenario {name} done: net_cost={metrics['net_cost']:.2f}, profit={metrics['profit']:.2f}, alpha={metrics['alpha']:.3f}")

# 5) Visualizations (examples)
# (a) bar: net cost / profit per scenario
names = list(results_summary.keys())
net_costs = [results_summary[n]["net_cost"] for n in names]
profits = [-nc for nc in net_costs]

plt.figure(figsize=(8,4))
plt.bar(names, net_costs)
plt.title("Net cost per scenario")
plt.ylabel("Net cost (DKK)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "net_costs.png"))
plt.close()

# (b) time series for a chosen scenario (e.g. price_spike)
sel = "price_spike"
m = results_summary[sel]
hours = np.arange(T)
plt.figure(figsize=(10,4))
plt.plot(hours, m["G"], label="PV_gen")
plt.plot(hours, m["L"], label="Load")
plt.plot(hours, m["I"], label="Import")
plt.plot(hours, m["X"], label="Export")
plt.plot(hours, m["C"], label="Curtail")
plt.legend()
plt.title(f"Time series - {sel}")
plt.xlabel("Hour")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, f"{sel}_timeseries.png"))
plt.close()

# (c) shadow prices lambda_t for each scenario (heatmap or multiple lines)
plt.figure(figsize=(10,4))
for name in names:
    plt.plot(hours, results_summary[name]["lambda_t"], label=name)
plt.legend()
plt.title("Shadow price (lambda_t) across scenarios")
plt.xlabel("Hour")
plt.ylabel("lambda_t (DKK/kWh)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "shadow_prices.png"))
plt.close()

# 6) Save summary results to CSV
df = pd.DataFrame({
    name: {
        "Net cost": metrics["net_cost"],
        "Profit": metrics["profit"],
        "Self-consumption": metrics["self_consumption_ratio"],
        "Exported": metrics["exported"],
        "Imported": metrics["imported"],
        "Alpha": metrics["alpha"]
    }
    for name, metrics in results_summary.items()
}).T

df.to_csv("src/output/question1a/scenario_summary.csv", index=True)
print(df)