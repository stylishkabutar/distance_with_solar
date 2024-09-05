'''
Helper functions 
'''
# Import necessary modules

import pandas as pd
import numpy as np
from d_solar import calc_solar_irradiance,calculate_incident_solarpower
from d_config import PANEL_AREA, PANEL_EFFICIENCY, BATTERY_CAPACITY, HR, KM
from d_setting import STEP, AVG_V, d_control_stops, RACE_DISTANCE, CONTROL_STOP_DURATION,FULL_DAY_TIME


# Helper functions

def set_at_sampling_rate(route_df):
    '''
    Pre-processes the route_df corresponding to sampling rate
    '''
    route_df['Altitude']=(np.tan(np.radians(route_df['Slope (deg)']))*route_df["StepDistance(m)"]).cumsum()
    for i in range(0, len(route_df), int(STEP * AVG_V)):
        route_df.loc[i: (i + int(STEP * AVG_V)),'Slope (deg)'] = (route_df['Slope (deg)'][i: (i + int(STEP * AVG_V))] * route_df['StepDistance(m)'][i: (i + int(STEP * AVG_V))]).sum() / (route_df['StepDistance(m)'][i: (i + int(STEP * AVG_V))]).sum()
        route_df.loc[i: (i + int(STEP * AVG_V)),'WindSpeed(m/s)'] = route_df['WindSpeed(m/s)'][i: (i + int(STEP * AVG_V))].mean()
        # route_df.loc[i: (i + int(STEP * AVG_V)),'Altitude'] = route_df['Altitude'][i]-route_df['Altitude'][ (i + int(STEP * AVG_V))]
        route_df.loc[i: (i + int(STEP * AVG_V)),'Winddirection(frmnorth)'] = np.arccos(np.cos(route_df['Winddirection(frmnorth)'][i: (i + int(STEP * AVG_V))]).mean())* 180 / np.pi
        route_df.loc[i: (i + int(STEP * AVG_V)),'Lattitude'] = route_df['Lattitude'][i: (i + int(STEP * AVG_V))].mean()
        route_df.loc[i: (i + int(STEP * AVG_V)),'Longitude'] = route_df['Longitude'][i: (i + int(STEP * AVG_V))].mean()

    route_df.to_csv("processed_route_data_final.csv", index = False)

def find_control_stops(run_dat):
    '''
    Find time at which control stops occur
    '''
    nearest_cum_dist = pd.merge_asof(pd.DataFrame({'Stop distances': d_control_stops}), run_dat['Cumulative Distance'], left_on = 'Stop distances',  right_on = 'Cumulative Distance', direction = 'nearest')
    result = pd.merge(nearest_cum_dist, run_dat, on = 'Cumulative Distance')
    
    return np.array(result['Time'])

def format_data(run_dat):
    '''
    Update model result with control stops
    '''

    time = find_control_stops(run_dat)
    i_list = []
    # print(time)
    for t in time:
        i = run_dat.index[run_dat['Time'] == t][0]
        i_list.append(i)
   
    #run_dat = run_dat.reset_index(drop = True)
    # Shift time
    for i in i_list:
        run_dat.loc[(i + 1):,'Time'] += CONTROL_STOP_DURATION
        # print(i_list,time)
    return run_dat


def add_control_stops(run_dat):
    ''' 
    Insert control stop data
    '''

    time = find_control_stops(run_dat)
    # print("tim-",time)
    i_list = []
    for t in time:
        i = run_dat.index[run_dat['Time'] == t][0]
        i_list.append(i)

    for i in i_list[::-1]:

        time_array = np.array([(run_dat.at[i, 'Time'] + j) for j in range(STEP, (CONTROL_STOP_DURATION + STEP), STEP)])
        acc_array = [0 for _ in range(len(time_array))]
        v_array = [0 for _ in range(len(time_array))]
        cum_d_array = [(run_dat.at[i, 'Cumulative Distance']) for _ in range(len(time_array))]
        solar_array =  np.array([((STEP/HR ) * calculate_incident_solarpower(k%(FULL_DAY_TIME),0,0)) for k in time_array])
        energy_consumption_array = [0 for _ in range(len(time_array))]
        battery_array = ((run_dat.at[i, 'Battery'] / 100 * BATTERY_CAPACITY) + solar_array.cumsum()) / BATTERY_CAPACITY * 100

        new_dat = pd.DataFrame({'Time': time_array, 'Velocity': v_array, 'Acceleration': acc_array, 'Battery': battery_array, 'EnergyConsumption': energy_consumption_array, 'Solar': solar_array, 'Cumulative Distance': cum_d_array})
        # print(new_dat)
        run_dat = pd.concat([run_dat, new_dat])
        
    run_dat = run_dat.sort_values(by = 'Time', ignore_index = True)
    
    return run_dat

def find_reachtime(cum_dt, cum_d):
    '''
    Find time at which race distance is crossed
    '''
    for i  in range(len(cum_d)):
        if cum_d[i] > (RACE_DISTANCE / KM):
            return cum_dt[i]
    return cum_dt[-1]