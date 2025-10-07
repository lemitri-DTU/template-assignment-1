"""
Placeholder for main function to execute the model runner. This function creates a single/multiple instance of the Runner class, prepares input data,
and runs a single/multiple simulation.

Suggested structure:
- Import necessary modules and functions.
- Define a main function to encapsulate the workflow (e.g. Create an instance of your the Runner class, Run a single simulation or multiple simulations, Save results and generate plots if necessary.)
- Prepare input data for a single simulation or multiple simulations.
- Execute main function when the script is run directly.
"""
import os
print(f"datapath: {os.path.abspath('../Group18_assignment_1/data/question_1a')}")

# main.py
from data_ops.data_loader import DataLoader
from opt_model.opt_model import OptModel

if __name__ == "__main__":
    loader = DataLoader("../Group18_assignment_1/data")
    loader.load_question1a()
    params = loader.get_params_for_q1a()

    model = OptModel(params)
    results = model.solve()

    for k, v in results.items():
        print(k, v)


# # main.py
# from data_ops.data_loader import DataLoader
# from opt_model.opt_model import OptModel

# if __name__ == "__main__":
#     # datapath
#     data_path = "../Group18_assignment_1/data"
#     question_name = "question_1a"

#     # initialize DataLoader
#     loader = DataLoader(input_path=data_path)

#     # Get OptModel parameters
#     params = loader.get_params_for_q1a(question_name)

#     # Initialize and solve optimization model
#     model = OptModel(params)
#     results = model.solve()

#     # Print results
#     if results:
#         print("\n--- Optimization results (first 5 hours) ---")
#         for k, v in results.items():
#             if k != "Objective":
#                 print(f"{k}: {v[:5]} ...")
#         print(f"Objective value: {results['Objective']:.2f} DKK")
