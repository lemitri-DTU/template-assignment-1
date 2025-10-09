# src/analysis/analysis_q1b.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))  # add src to path

import numpy as np
import os
import matplotlib.pyplot as plt
from data_ops.data_loader import DataLoader
from opt_model.opt_model_b import OptModelFlex  

OUTPUT_DIR = Path("src/output/question1b")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1) load data
loader = DataLoader(Path("data"))
loader.load_question1b()
params = loader.get_params_for_q1b()

T = int(params["T"])

# 2) choose a reference profile Lref
# Option A: uniform preferred consumption (e.g. 8 kWh/day distributed evenly)
# Option B: use a simple temporal preference (peak at evening)
# I show two options; pick one or try both.
Lref_uniform = np.full(T, 8.0 / T)   # total 8 kWh/day distributed evenly
# evening-peaked reference (example):
Lref_evening = np.zeros(T)
peak_hour = min(18, T-1)
Lref_evening[peak_hour] = 4.0
Lref_evening[peak_hour-1 if peak_hour>0 else peak_hour] = 2.0
# ensure length T
Lref_evening = Lref_evening

# 3) define preference scenarios (alpha small/medium/large)
scenarios = {
    "alpha_small": {"alpha": 0.01, "Lref": Lref_uniform},
    "alpha_medium": {"alpha": 1.0, "Lref": Lref_uniform},
    "alpha_large": {"alpha": 100.0, "Lref": Lref_evening},
}

results = {}
for name, cfg in scenarios.items():
    print(f"Running scenario {name}, alpha={cfg['alpha']}")
    model = OptModelFlex(params, Lref=cfg["Lref"], alpha=cfg["alpha"])
    sol = model.solve(verbose=False)
    duals = model.get_duals()
    results[name] = {"sol": sol, "duals": duals, "cfg": cfg}

# 4) save a simple summary table and print
import pandas as pd
rows = []
for name, r in results.items():
    sol = r["sol"]
    total_import = sol["I"].sum()
    total_export = sol["X"].sum()
    total_pv = sol["G"].sum()
    self_consumed = np.maximum(sol["G"] - sol["X"], 0).sum()
    self_cons_ratio = (self_consumed / total_pv) if total_pv>0 else 0.0
    rows.append({
        "scenario": name,
        "alpha": r["cfg"]["alpha"],
        "obj": sol["obj"],
        "total_import": total_import,
        "total_export": total_export,
        "total_pv": total_pv,
        "self_consumption_ratio": self_cons_ratio
    })
df = pd.DataFrame(rows).set_index("scenario")
df.to_csv(OUTPUT_DIR / "scenario_summary_q1b.csv")
print(df)

# 5) plots (save, do not show)
hours = np.arange(T)
for name, r in results.items():
    sol = r["sol"]
    plt.figure(figsize=(10,4))
    plt.plot(hours, sol["L"], label="Load")
    plt.plot(hours, sol["G"], label="PV_gen")
    plt.plot(hours, sol["I"], label="Import")
    plt.plot(hours, sol["X"], label="Export")
    plt.title(f"Energy flows - {name} (alpha={r['cfg']['alpha']})")
    plt.xlabel("Hour")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"time_series_{name}.png")
    plt.close()

# duals plot (lambda_t)
plt.figure(figsize=(10,4))
for name, r in results.items():
    lambda_t = r["duals"]["lambda_t"]
    plt.plot(hours, lambda_t, label=f"{name} (alpha={r['cfg']['alpha']})")
plt.legend()
plt.title("Shadow prices lambda_t across preference scenarios")
plt.xlabel("Hour")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "lambda_t_q1b.png")
plt.close()

print("Plots and summary saved to", OUTPUT_DIR)
