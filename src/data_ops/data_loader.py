# -----------------------------
# Load Data
# -----------------------------
import json
import csv
import pandas as pd
from pathlib import Path

from pathlib import Path
from dataclasses import dataclass
from logging import Logger
import pandas as pd
import xarray as xr
import numpy as np
# import yaml

from pathlib import Path
import json
import numpy as np

class DataLoader:
    """
    DataLoader for Question 1(a) of the assignment.
    Loads JSON files from a given input path and converts them
    into parameters suitable for the optimization model.
    """

    def __init__(self, input_path):
        self.input_path = Path(input_path)
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input path {self.input_path} does not exist")

    def _load_json(self, filename, question_name=None):
        """
        Load a JSON file. If question_name is provided, look into that subfolder.
        """
        if question_name:
            filepath = self.input_path / question_name / filename
        else:
            filepath = self.input_path / filename
        if not filepath.exists():
            raise FileNotFoundError(f"{filename} not found in {filepath.parent}")
        with open(filepath, 'r') as f:
            return json.load(f)

    def load_question1a(self):
        """
        Load all required JSON files for Question 1(a).
        """
        question_name = "question_1a"
        self.appliance_params = self._load_json("appliance_params.json", question_name)
        self.consumer_params = self._load_json("consumer_params.json", question_name)
        self.DER_production = self._load_json("DER_production.json", question_name)
        self.usage_preference = self._load_json("usage_preference.json", question_name)
        print("All JSON files loaded for question1a.")

    def get_params_for_q1a(self):
        """
        Convert loaded JSON data into parameters usable by OptModel.
        Returns a dictionary with keys: T, pv_max, p, g, E_min, c_pv
        """
        # PV maximum available per hour
        pv_max_power = self.appliance_params["DER"][0]["max_power_kW"]
        pv_profile = np.array(self.DER_production[0]["hourly_profile_ratio"])
        pv_max = pv_max_power * pv_profile  # kWh per hour

        # Minimum daily energy consumption
        E_min = self.usage_preference[0]["load_preferences"][0]["min_total_energy_per_day_hour_equivalent"]

        # Number of time steps
        T = len(pv_max)

        # Hourly electricity price and grid tariff (example placeholders)
        p = np.linspace(1.0, 3.0, T)      # Replace with actual price data if available
        g = np.full(T, 0.2)                # Replace with actual grid tariff if available

        # PV marginal cost (assumed zero)
        # c_pv = np.ones(T)
        c_pv = np.full(T, 2)    # when it's 0 and 1, the objective are minus, when it's 2 it's positive.


        params = {
            "T": T,
            "pv_max": pv_max,
            "p": p,
            "g": g,
            "E_min": E_min,
            "c_pv": c_pv
        }

        print("T =", params["T"])
        print("pv_max =", params["pv_max"])
        print("p =", params["p"])
        print("g =", params["g"])
        print("E_min =", params["E_min"])
        print("c_pv =", params["c_pv"])

        # return params

    def load_question1b(self):
        """
        Load all required JSON files for Question 1(b).
        Same structure as Question 1(a), but usage_preference.json now includes
        hourly reference load profile instead of a fixed minimum energy requirement.
        """
        question_name = "question_1b"
        self.appliance_params = self._load_json("appliance_params.json", question_name)
        self.consumer_params = self._load_json("consumer_params.json", question_name)
        self.DER_production = self._load_json("DER_production.json", question_name)
        self.usage_preferences = self._load_json("usage_preferences.json", question_name)
        print("All JSON files loaded for question1b.")


    def get_params_for_q1b(self):
        """
        Convert loaded JSON data into parameters usable by OptModelFlex (for Question 1b).
        Returns a dictionary with keys: T, pv_max, p, g, c_pv, L_ref, alpha
        """
        import numpy as np

        # PV maximum available per hour
        pv_max_power = self.appliance_params["DER"][0]["max_power_kW"]
        pv_profile = np.array(self.DER_production[0]["hourly_profile_ratio"])
        pv_max = pv_max_power * pv_profile  # kWh per hour

        # Reference load profile from usage_preference.json
        L_ref_ratio = np.array(self.usage_preferences[0]["load_preferences"][0]["hourly_profile_ratio"])
        L_ref = L_ref_ratio / L_ref_ratio.max() * 10  # scale to a reasonable magnitude (e.g., 0–10 kWh)

        # Number of time steps
        T = len(pv_max)

        # Hourly electricity price and grid tariff
        p = np.linspace(1.0, 3.0, T)      # price [€/kWh]
        g = np.full(T, 0.2)               # grid tariff [€/kWh]

        # PV marginal cost (assumed small positive)
        c_pv = np.full(T, 2)

        # Discomfort penalty weight (α): can test multiple scenarios later
        alpha = 1.0

        params = {
            "T": T,
            "pv_max": pv_max,
            "p": p,
            "g": g,
            "c_pv": c_pv,
            "L_ref": L_ref,
            "alpha": alpha
        }

        print("T =", params["T"])
        print("pv_max =", params["pv_max"])
        print("p =", params["p"])
        print("g =", params["g"])
        print("c_pv =", params["c_pv"])
        print("L_ref =", params["L_ref"])
        print("alpha =", params["alpha"])

        return params
