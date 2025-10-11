# src/main.py
import os
from data_ops.data_loader import DataLoader
from opt_model.opt_model import OptModel          # Question 1a
from opt_model.opt_model_b import OptModelFlex    # Question 1b
from opt_model.opt_model_c import OptModelBattery # Question 1c

if __name__ == "__main__":
    question = "1c"   # switch between "1a", "1b", "1c"

    data_dir = "../Group18_assignment_1/data"
    loader = DataLoader(data_dir)

    if question == "1a":
        print(f"Loading data for Question 1a from: {os.path.abspath(os.path.join(data_dir, 'question_1a'))}")
        loader.load_question1a()
        params = loader.get_params_for_q1a()
        model = OptModel(params)
        results = model.solve()

        print("\n=== RESULTS FOR QUESTION 1A ===")
        for k, v in results.items():
            print(k, v)

    elif question == "1b":
        print(f"Loading data for Question 1b from: {os.path.abspath(os.path.join(data_dir, 'question_1b'))}")
        loader.load_question1b()
        params = loader.get_params_for_q1b()

        # Example scenario: you can modify alpha & Lref here or load from JSON
        alpha = 1.0
        Lref = params.get("L_ref", [8.0/params["T"]]*params["T"])  # fallback uniform load
        model = OptModelFlex(params, Lref=Lref, alpha=alpha)
        results = model.solve()

        print("\n=== RESULTS FOR QUESTION 1B ===")
        for k, v in results.items():
            print(k, v)

    elif question == "1c":
        print(f"Loading data for Question 1c from: {os.path.abspath(os.path.join(data_dir, 'question_1b'))}")
        loader.load_question1b()  # 1c uses same input as 1b
        params = loader.get_params_for_q1b()

        # Example: define reference load & battery parameters
        alpha = 1.0
        T = params["T"]
        Lref = [8.0/T]*T
        battery_params = {
            "S_max":5.0, "S_min":0.0,
            "P_ch_max":2.0, "P_dis_max":2.0,
            "eta_ch":0.95, "eta_dis":0.95,
            "s0":2.5, "c_bat":0.0
        }
        model = OptModelBattery(params, Lref=Lref, alpha=alpha, battery_params=battery_params)
        results = model.solve()

        print("\n=== RESULTS FOR QUESTION 1C ===")
        for k, v in results.items():
            print(k, v)

    else:
        raise ValueError("question must be '1a', '1b' or '1c'")






# """
# Placeholder for main function to execute the model runner. This function creates a single/multiple instance of the Runner class, prepares input data,
# and runs a single/multiple simulation.

# Suggested structure:
# - Import necessary modules and functions.
# - Define a main function to encapsulate the workflow (e.g. Create an instance of your the Runner class, Run a single simulation or multiple simulations, Save results and generate plots if necessary.)
# - Prepare input data for a single simulation or multiple simulations.
# - Execute main function when the script is run directly.
# """
# # #main.py only for question 1a
# # import os
# # print(f"datapath: {os.path.abspath('../Group18_assignment_1/data/question_1a')}")

# # # main.py
# # from data_ops.data_loader import DataLoader
# # from opt_model.opt_model import OptModel

# # if __name__ == "__main__":
# #     loader = DataLoader("../Group18_assignment_1/data")
# #     loader.load_question1a()
# #     params = loader.get_params_for_q1a()

# #     model = OptModel(params)
# #     results = model.solve()

# #     for k, v in results.items():
# #         print(k, v)

# # main.py which can switch between question 1a and 1b
# # src/main.py
# import os
# from data_ops.data_loader import DataLoader
# from opt_model.opt_model import OptModel
# from opt_model.opt_model_b import OptModelFlex  # model for question 1b

# if __name__ == "__main__":
#     question = "1b"   # switch between "1a" and "1b"

#     if question == "1a":
#         print(f"datapath: {os.path.abspath('../Group18_assignment_1/data/question_1a')}")
#         loader = DataLoader("../Group18_assignment_1/data")
#         loader.load_question1a()
#         params = loader.get_params_for_q1a()

#         model = OptModel(params)
#         results = model.solve()

#         print("\n=== RESULTS FOR QUESTION 1A ===")
#         for k, v in results.items():
#             print(k, v)

#     elif question == "1b":
#         print(f"datapath: {os.path.abspath('../Group18_assignment_1/data/question_1b')}")
#         loader = DataLoader("../Group18_assignment_1/data")
#         loader.load_question1b()
#         params = loader.get_params_for_q1b()

#         # assume params includes 'L_ref' and 'alpha' for question 1b
#         model = OptModelFlex(params, Lref=params["L_ref"], alpha=params["alpha"])
#         results = model.solve()

#         print("\n=== RESULTS FOR QUESTION 1B ===")
#         for k, v in results.items():
#             print(k, v)

#     else:
#         raise ValueError("question must be '1a' or '1b'")
