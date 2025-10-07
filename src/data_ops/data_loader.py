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

        return params

# class DataLoader:
#     """Loads energy system input data and prepares parameters for optimization."""

#     def __init__(self, input_path=None):
#         self.input_path = Path(input_path) if input_path else None

#     def _load_dataset(self, question_name: str):
#         """Load all relevant JSON files for the question."""
#         question_path = self.input_path / question_name
#         if not question_path.exists():
#             raise FileNotFoundError(f"Question folder {question_path} not found.")

#         expected_files = [
#             'appliance_params.json',
#             'bus_params.json',
#             'consumer_params.json',
#             'DER_production.json',
#             'usage_preference.json'
#         ]
#         for fname in expected_files:
#             fpath = question_path / fname
#             if fpath.exists():
#                 with open(fpath, 'r') as f:
#                     data = json.load(f)
#                     setattr(self, fname.replace('.json', ''), data)

#     def get_params_for_q1a(self, question_name: str):
#         """
#         Extract parameters for OptModel for Question 1(a).
#         Returns a dictionary ready to pass to OptModel.
#         """
#         # Load JSON files
#         self._load_dataset(question_name)

#         # --- PV ---
#         app = self.appliance_params
#         der = self.DER_production
#         usage = self.usage_preference

#         max_pv_power = app["DER"][0]["max_power_kW"]
#         pv_profile = np.array(der[0]["hourly_profile_ratio"])
#         pv_max = max_pv_power * pv_profile

#         # --- Load ---
#         E_min = usage[0]["load_preferences"][0]["min_total_energy_per_day_hour_equivalent"]
#         max_load = app["load"][0]["max_load_kWh_per_hour"]

#         # --- Prices and grid tariffs ---
#         T = len(pv_max)
#         p = np.linspace(1.0, 3.0, T)   # replace with real prices if available
#         g = np.full(T, 0.2)             # flat grid tariff

#         # --- Return params dictionary ---
#         params = {
#             "T": T,
#             "p": list(p),
#             "g": list(g),
#             "pv_max": list(pv_max),
#             "E_min": float(E_min),
#             "max_load": float(max_load)
#         }
#         return params



    # def _load_data_file(self, question_name: str, file_name: str):
    #     """
    #     Placeholder function 
    #     Helper function to load a specific CSV or json file, using the appropriate method based on file extension.. Raises FileNotFoundError if missing.
        
    #     example usage: 
    #     define and call a load_data_file() function from utils.py to load a specific file in the input_path directory
    #     save all data as class attributes (e.g. self.demand, self.wind, etc.), structured as pandas DataFrames or Series (or other format as prefered)"""
    #     pass

    # def load_aux_data(self, question_name: str, filename: str):
    #     """
    #     Placeholder Helper function to Load auxiliary metadata for the scenario/question from a YAML/json file or other formats
        
    #     Example application: 
    #     define and call a load_aux_data() function from utils.py to load a specific auxiliary file in the input_path directory
    #     Save the content as s class attributes, in a dictionary, pd datframe or other: self.aux_data
    #     Attach key values as class attributes (flattened).
    #     """
    #     pass