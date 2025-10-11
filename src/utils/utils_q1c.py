import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from data_ops.data_loader import DataLoader
from opt_model.opt_model_c import OptModelBattery

OUTPUT_DIR = Path("src/output/question1c")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
loader = DataLoader(Path("data"))
loader.load_question1b()
params = loader.get_params_for_q1b()
T = int(params["T"])

# Reference load and alpha scenarios
Lref_uniform = np.full(T, 8.0/T)
Lref_evening = np.zeros(T)
Lref_evening[16] = 2.0
Lref_evening[17] = 4.0

scenarios = {
    "alpha_small": {"alpha":0.01, "Lref": Lref_uniform},
    "alpha_medium":{"alpha":1.0, "Lref": Lref_uniform},
    "alpha_large":{"alpha":100.0, "Lref": Lref_evening},
}

battery_params = {
    "S_max":5.0, "S_min":0.0,
    "P_ch_max":2.0, "P_dis_max":2.0,
    "eta_ch":0.95, "eta_dis":0.95,
    "s0":2.5, "c_bat":0.0
}

results = {}
for name, cfg in scenarios.items():
    print(f"Running {name}")
    model = OptModelBattery(params, Lref=cfg["Lref"], alpha=cfg["alpha"], battery_params=battery_params)
    res = model.solve(verbose=False)
    results[name] = {"res": res, "cfg": cfg}

# Save summary table
rows = []
for name, r in results.items():
    res = r["res"]
    total_import = res["I"].sum()
    total_export = res["X"].sum()
    total_pv = res["G"].sum()
    self_cons = np.maximum(res["G"] - res["X"],0).sum()
    total_discharge = res["P_dis"].sum()
    total_charge = res["P_ch"].sum()
    rows.append({
        "scenario": name,
        "alpha": r["cfg"]["alpha"],
        "obj": res["obj"],
        "total_import": total_import,
        "total_export": total_export,
        "total_pv": total_pv,
        "self_consumed": self_cons,
        "total_charge": total_charge,
        "total_discharge": total_discharge
    })
df = pd.DataFrame(rows).set_index("scenario")
df.to_csv(OUTPUT_DIR / "scenario_summary_q1c.csv")
print(df)

# Plot example
hours = np.arange(T)
for name, r in results.items():
    res = r["res"]
    plt.figure(figsize=(10,4))
    plt.plot(hours, res["L"], label="Load")
    plt.plot(hours, res["G"], label="PV_gen")
    plt.plot(hours, res["I"], label="Import")
    plt.plot(hours, res["X"], label="Export")
    plt.plot(hours, res["P_dis"], label="Battery Discharge")
    plt.plot(hours, res["P_ch"], label="Battery Charge")
    plt.plot(hours, res["S"][:-1], "--", label="SoC")
    plt.xlabel("Hour")
    plt.ylabel("kWh")
    plt.title(f"Energy flows + battery - {name}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"time_series_batt_{name}.png")
    plt.close()
print("All results and plots saved to", OUTPUT_DIR)

# Plot objective per scenario
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = Path("src/output/question1c")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Your results table
scenarios = ["alpha_small", "alpha_medium", "alpha_large"]
obj_values = [-29.17999695, -26.53999693, -13.72065884]  # replace with your actual results

plt.figure(figsize=(8, 5))
plt.bar(scenarios, obj_values, color=['skyblue', 'salmon', 'limegreen'])
plt.ylabel("Objective (Net cost/profit in DKK)")
plt.title("Objective function (net cost/profit) for each scenario with battery integration")
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Save figure
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "obj_per_scenario_q1c.png")
plt.close()
print(f"Figure saved at {OUTPUT_DIR / 'obj_per_scenario_q1c.png'}")
