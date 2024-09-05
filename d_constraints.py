'''
Constraints, bounds and objective for the model
'''
# Import necessary modules

import numpy as np
import pandas as pd
from d_config import BATTERY_CAPACITY, DISCHARGE_CAP, MAX_V,  MAX_CURRENT, BUS_VOLTAGE, HR,K
from d_setting import CONTROL_STOP_DURATION,RACE_START,DT_list_day,RunforDays, STEP
from d_car_dynamics import calculate_dx, calculate_power_req, convert_domain_d2t
from d_solar import calculate_incident_solarpower, Solar
from d_offrace_solarcalc import calculate_energy
from d_helper_fns import find_control_stops
df1 = pd.read_csv('locations_set.csv')
df2 = pd.read_csv('normals_set.csv')
df3 = pd.read_csv('areas_set.csv')
df_buf = pd.concat([df1, df2, df3], axis=1)
solar=Solar(df_buf)
# Define constants
SAFE_BATTERY_LEVEL = BATTERY_CAPACITY * DISCHARGE_CAP
MAX_P = BUS_VOLTAGE * MAX_CURRENT

# Bounds for the velocity
def get_bounds(N):
    '''
    Velocity bounds throughout the race
    '''
    return ([(0, 0)] + [(0.01, MAX_V)] * (N-2) + [(0, 0)]) # Start and end velocity is zero
#def control_stop_constraint(v,cumd):
    
   
    #if v[find_control_stops_v(v,cumd)]!=None:
 #   k=v[list(find_control_stops_v(v,cumd))]
    
  #  return -np.linalg.norm(-v[(find_control_stops_v(v,cumd))])
    #else:
     #   return 0

def objective(velocity_profile, dt, cum_d_array, slope_array, lattitude_array, longitude_array, cum_d, i, InitialBatteryCapacity, FinalBatteryCapacity, wind_speed, wind_direction):
    '''
    Maximize total distance travelled
    '''
    dx = calculate_dx(velocity_profile[:-1], velocity_profile[1:], dt)
    #Min_B, B_bar = battery_and_acc_constraint(velocity_profile, dt, cum_d_array, slope_array, lattitude_array, longitude_array)

    # return np.abs(3055 * 10**3 - cum_d - np.sum(dx)) 
    discharge, overcharge, max_p, final_bat= battery_and_acc_constraint(velocity_profile, dt, cum_d_array, slope_array, lattitude_array, longitude_array, cum_d, i, InitialBatteryCapacity, FinalBatteryCapacity, wind_speed, wind_direction)

    return - np.sum(dx) + 10 ** 3 * abs(final_bat) - discharge * (RunforDays-i) * 10 ** 2#+ np.max(-Min_B * 10 ** 16, 0) + np.max(-B_bar * 10 ** 12, 0)

def battery_and_acc_constraint(velocity_profile, dt, cum_d_array, slope_array, lattitude_array, longitude_array, cum_d, i, InitialBatteryCapacity, FinalBatteryCapacity, wind_speed, wind_direction):
    '''
    Battery safety and acceleration constraint
    '''

    dx = calculate_dx(velocity_profile[:-1], velocity_profile[1:], dt)
     
    slope_array, lattitude_array, longitude_array,wind_speed_array,wind_direction_array = convert_domain_d2t(velocity_profile, pd.DataFrame({'CumulativeDistance(km)': cum_d_array, 'Slope': slope_array, 'Lattitude': lattitude_array, 'Longitude': longitude_array,'WindSpeed(m/s)':wind_speed,"Winddirection(frmnorth)":wind_direction }), dt)

    start_speeds, stop_speeds = velocity_profile[:-1], velocity_profile[1:]

    acceleration = (stop_speeds - start_speeds) / dt
    avg_speed = (start_speeds + stop_speeds) / 2
   
    altitude_array=(np.tan(np.radians(slope_array))*dx).cumsum()
    

    # Find control stops
    cum_dtot = dx.cumsum() + cum_d * K
    
    cum_dtot=cum_dtot / K
    cum_t = dt.cumsum() + DT_list_day[i]
    dfx=pd.DataFrame({'Cumulative Distance': cum_dtot, 'Time': cum_t})
   
    control_stop_array =  find_control_stops((dfx))
    
      
    #Solar correction
    indices = [np.searchsorted(dt.cumsum() , t - DT_list_day[i], side = 'right') for t in control_stop_array ]
    # print("chilla",[t-i*DT for t in control_stop_array])

    # print("control stops my igga",control_stop_array)
    # print("control-spto",indices)
    dt1 = np.copy(dt)
    indices=[i for i in indices if i<len(avg_speed) and i != 0 and i != 1]
    # print("ssss",indices)
    for idx in indices:
        if idx < len(dt1) and idx != 0:
            dt1[idx] += CONTROL_STOP_DURATION


    P_req, _ = calculate_power_req(avg_speed, acceleration, slope_array, wind_speed_array, wind_direction_array)
    _, P_solar = solar.Energy_Array_Racing(0, 0, lattitude_array, longitude_array, altitude_array, dt1, RACE_START, i, 232)
   # P_solar = calculate_incident_solarpower(dt1_cumsum, lattitude_array, longitude_array)
    
    
    energy_consumed = ((P_req/ HR - np.array(P_solar['power'])) * dt).cumsum()
    # energy_consumed = energy_consumed
    # Add energy gained through control stop
    
    k=2*i
    for id, gt in enumerate(control_stop_array[range(0,len(indices))]):
        # print(id,indices[id])
        t = int((gt+k * CONTROL_STOP_DURATION) % (RunforDays * HR))
        # alpha,beta, _ = solar.Tilt_Angle(t + RACE_START, t + CONTROL_STOP_DURATION +  RACE_START, 232, lattitude_array[id], longitude_array[id], altitude_array[id])
        control_stop_E, _ =solar.Energy_Array_Racing(0,0, lattitude_array[id], longitude_array[id], altitude_array[id], np.array(range(t + RACE_START, t + CONTROL_STOP_DURATION +  RACE_START,STEP)), t + RACE_START, i, d=232)

        energy_consumed[indices[id]:] -= control_stop_E
        k+=1
     # Wh

    battery_profile = InitialBatteryCapacity - energy_consumed - SAFE_BATTERY_LEVEL
    final_battery_lev = InitialBatteryCapacity - energy_consumed[-1] - FinalBatteryCapacity

    return np.min(battery_profile),(BATTERY_CAPACITY - SAFE_BATTERY_LEVEL) - np.max(battery_profile), MAX_P - np.max(P_req - P_solar['power']),1000* final_battery_lev # Ensure battery level bounds
    
# def v_end(velocity_profile, dt, cum_d):
#     dx = calculate_dx(velocity_profile[:-1], velocity_profile[1:], dt)
#     d = cum_d + np.sum(dx)
#     return (3050 * 10 **3 - d) * np.min(velocity_profile), np.min(velocity_profile)

