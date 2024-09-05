'''
Run day-wise distance optimization model for multiple days
'''

# Import necessary modules

import pandas as pd
import numpy as np
from d_setting import set_day, RunforDays
from d_config import HR, BATTERY_CAPACITY
from d_model import main
from d_offrace_solarcalc import calculate_energy
from d_solar import Solar
df1 = pd.read_csv('locations_set.csv')
df2 = pd.read_csv('normals_set.csv')
df3 = pd.read_csv('areas_set.csv')
df_buf = pd.concat([df1, df2, df3], axis=1)
route_df = pd.read_csv("processed_route_data_final.csv")
df_list = []
solar=Solar(df_buf)
# time_counter = 0
v_avg = 0

k=0
for i in range(RunforDays):
    if i == 0:
        present_battery_cent = 100
        stop_gain = 0
        cum_d = 0
    else:
        present_battery_cent = np.array(outdf['Battery'])[-1]
        print(present_battery_cent)
        cum_d = np.array(outdf['Cumulative Distance'])[-1]
        stop_gain = calculate_energy(6 * HR, 8 * HR) + calculate_energy(17 * HR, 18 * HR) # 6AM - 8AM, 5PM - 6PM

        present_battery_cent = min(present_battery_cent + ((stop_gain ) / BATTERY_CAPACITY) * 100, 100) # Neglect excess stop gain 
        print(present_battery_cent)
    InitialBatteryCapacity, FinalBatteryCapacity,DT = set_day(present_battery_cent, i) #, time_counter) # timeoffset = 
    
    outdf, timetaken = main(DT,k,route_df, cum_d, i, InitialBatteryCapacity, FinalBatteryCapacity) # Set day wise params

    outdf['Time'] = outdf['Time'] + k
    k+=DT
    outdf['Cumulative Distance'] += cum_d 
    df_list.append(outdf)

    # time_counter += timetaken

dfnet = pd.concat(df_list)
dfnet.to_csv('raw_run_dat.csv', index=False)
print(f"Written {RunforDays} days data to `raw_run_dat.csv`")