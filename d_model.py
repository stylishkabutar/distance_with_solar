'''
Main day-wise model
'''

# Import necessary modules
import numpy as np
from scipy.optimize import minimize
import pandas as pd
from d_config import KM, HR
from d_car_dynamics import calculate_dx
from d_setting import ModelMethod, InitialGuessVelocity, STEP
from d_constraints import get_bounds, objective, battery_and_acc_constraint #, v_end
from d_profiles import extract_profiles



def main(DT,k,route_df, cum_d, i, InitialBatteryCapacity, FinalBatteryCapacity):
    
    step = STEP
    N = DT // step
    dt = np.full(int(N), step) # Set race time scale

    # Get data
    cum_d_array = route_df.iloc[:, 1].to_numpy()
    slope_array = route_df.iloc[:, 2].to_numpy()
    lattitude_array = route_df.iloc[:, 3].to_numpy()
    longitude_array = route_df.iloc[:, 4].to_numpy()
    wind_speed = route_df.iloc[:, 5].to_numpy()
    wind_direction= route_df.iloc[:, 6].to_numpy()
    N_V = int(N) + 1
    
    initial_velocity_profile = np.concatenate((np.array([0]), np.ones(N_V - 2) * InitialGuessVelocity, np.array([0])))

    bounds = get_bounds(N_V)

    constraints = [
        {
            "type": "ineq",
            "fun": battery_and_acc_constraint,
            "args": (
                  dt, cum_d_array, slope_array, lattitude_array, longitude_array, cum_d, i, InitialBatteryCapacity, FinalBatteryCapacity, wind_speed, wind_direction
            )
        }
     ]


    print("Starting Optimisation")

    optimised_velocity_profile = minimize(
        objective, 
        initial_velocity_profile,
        args = ( dt, cum_d_array, slope_array, lattitude_array, longitude_array, cum_d, i, InitialBatteryCapacity, FinalBatteryCapacity, wind_speed, wind_direction),

        bounds = bounds,
        method = ModelMethod,
        constraints = constraints,
        options = {'catol': 10 ** -6, 'disp': True, 'maxiter': 300}# "rhobeg":5.0}
        #options = {'maxiter': 3}
    )

    # optimised_velocity_profile = fmin_cobyla(
    #     objective,
    #     initial_velocity_profile,
    #     constraints,
    #     (),
    #     rhobeg,
    #     rhoend,
    #     maxfun,

    # )
    optimised_velocity_profile = np.array(optimised_velocity_profile.x) * 1 # derive the velocity profile

    dx = calculate_dx(optimised_velocity_profile[:-1], optimised_velocity_profile[1:], dt) # Find total distance travelled
    distance_travelled = np.sum(dx) / KM # km

    print("done.")
    print("Total distance travelled in day", (i+1), " :", distance_travelled, "km in travel time:", dt.sum() / HR, 'hrs')

   
  
    outdf = pd.DataFrame(
        dict(zip(
            ['Time', 'Velocity', 'Acceleration', 'Battery', 'EnergyConsumption', 'Solar', 'Cumulative Distance'],
            extract_profiles(k,optimised_velocity_profile, dt, cum_d_array, slope_array, lattitude_array, longitude_array, cum_d, i, InitialBatteryCapacity, wind_speed, wind_direction)
        ))
    )
    outdf['Cumulative Distance'] = np.concatenate([[0], dx.cumsum() / KM])
    return outdf, dt.sum()

# if __name__ == "__main__":
#     outdf, _ = main(route_df)
#     outdf.to_csv('run_dat.csv', index=False)

#     print("Written results to `run_dat.csv`")