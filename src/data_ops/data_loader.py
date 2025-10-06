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


class DataLoader:
    """
    Loads energy system input data for a given configuration/question from structured CSV and json files
    and an auxiliary configuration metadata file.
    
    Example usage:
    open interactive window in VSCode,
    >>> cd ../../
    run the script data_loader.py in the interactive window,
    >>> data = DataLoader(input_path='..')
    """
    question: str
    input_path: Path

    def __init__(self, input_path=None):
        """
        Post-initialization to load and validate all required datasets (placeholder function)

        example usage:
        self.input_path = Path(self.input_path).resolve()
        
        # Load metadata (auxiliary scenario data)
        self.load_aux_data('question1a_scenario1_aux_data.yaml')
        
        # Load CSV and json datasets
        self.data()
        """
        self.input_path = Path(input_path) if input_path else None
        # pass

    def _load_dataset(self, question_name: str):
        """Helper function to load all CSV or json files, using the appropriate method based on file extension.
        
        example usage: 
        call the load_dataset() function from utils.py to load all files in the input_path directory
        save all data as class attributes (e.g. self.demand, self.wind, etc.), structured as pandas DataFrames or Series (or other format as prefered)
        """
        question_path = Path(self.input_path) / question_name
        if not question_path.exists():
            raise FileNotFoundError(f"Question folder {question_path} not found.")

        expected_files = [
            'appliance_params.json',
            'bus_params.json',
            'consumer_params.json',
            'DER_production.json',
            'usage_preference.json',
            'usage_preferences.json'
        ]

        for fname in expected_files:
            fpath = question_path / fname
            if fpath.exists():
                with open(fpath, 'r') as f:
                    data = json.load(f)
                attr_name = fname.replace('.json', '')
                setattr(self, attr_name, data)

        loaded = [fname.replace('.json', '') for fname in expected_files if (question_path / fname).exists()]
        print(f"Loaded data for question '{question_name}': {loaded}")
        # pass

    def get_params_for_q1a(self, question_name: str):
        """
        Extracts key parameters for Question 1(a) based on the loaded dataset.
        Returns a dict ready for the OptModel class.
        """
        self._load_dataset(question_name)
        base = Path(self.input_path) / question_name

        # Extract info from loaded JSONs
        app = self.appliance_params
        der = self.DER_production
        usage = self.usage_preference

        # PV: maximum power * hourly production ratio
        max_pv_power = app["DER"][0]["max_power_kW"]
        pv_profile = np.array(der[0]["hourly_profile_ratio"])
        pv_max = max_pv_power * pv_profile  # kWh per hour

        # Load flexibility and daily min energy
        E_min = usage[0]["load_preferences"][0]["min_total_energy_per_day_hour_equivalent"]
        max_load = app["load"][0]["max_load_kWh_per_hour"]

        # Example: 24 hourly prices and tariffs (create placeholder arrays)
        T = len(pv_max)
        p = np.linspace(1.0, 3.0, T)        # DKK/kWh (you'll replace with real price data)
        g = np.full(T, 0.2)                 # DKK/kWh (flat grid tariff)

        params = {
            "T": T,
            "p": p,
            "g": g,
            "pv_max": pv_max,
            "E_min": E_min,
            "max_load": max_load
        }
        return params


    def _load_data_file(self, question_name: str, file_name: str):
        """
        Placeholder function 
        Helper function to load a specific CSV or json file, using the appropriate method based on file extension.. Raises FileNotFoundError if missing.
        
        example usage: 
        define and call a load_data_file() function from utils.py to load a specific file in the input_path directory
        save all data as class attributes (e.g. self.demand, self.wind, etc.), structured as pandas DataFrames or Series (or other format as prefered)"""
        pass

    def load_aux_data(self, question_name: str, filename: str):
        """
        Placeholder Helper function to Load auxiliary metadata for the scenario/question from a YAML/json file or other formats
        
        Example application: 
        define and call a load_aux_data() function from utils.py to load a specific auxiliary file in the input_path directory
        Save the content as s class attributes, in a dictionary, pd datframe or other: self.aux_data
        Attach key values as class attributes (flattened).
        """
        pass