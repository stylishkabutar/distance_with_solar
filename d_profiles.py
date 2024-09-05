import numpy as np
import pandas as pd
from d_config import BATTERY_CAPACITY, HR,K
from d_setting import  CONTROL_STOP_DURATION,RACE_START, DT_list_day,RunforDays, STEP
from d_car_dynamics import calculate_power_req, convert_domain_d2t, calculate_dx
from d_solar import calculate_incident_solarpower, Solar
from d_offrace_solarcalc import calculate_energy
from d_helper_fns import find_control_stops
df1 = pd.read_csv('locations_set.csv')
df2 = pd.read_csv('normals_set.csv')
df3 = pd.read_csv('areas_set.csv')
df_buf = pd.concat([df1, df2, df3], axis=1)
solar=Solar(df_buf)
def extract_profiles(k, velocity_profile, dt, cum_d_array, slope_array, lattitude_array, longitude_array, cum_d, i, InitialBatteryCapacity, wind_speed, wind_direction):
    # convert data to time domain
    slope_array, lattitude_array, longitude_array, wind_speed_array, wind_direction_array = convert_domain_d2t(velocity_profile, pd.DataFrame({'CumulativeDistance(km)': cum_d_array, 'Slope': slope_array, 'Lattitude': lattitude_array, 'Longitude': longitude_array,'WindSpeed(m/s)':wind_speed,'Winddirection(frmnorth)':wind_direction }), dt)

    start_speeds, stop_speeds = velocity_profile[:-1], velocity_profile[1:]
    
    avg_speed = (start_speeds + stop_speeds) / 2
    acceleration = (stop_speeds - start_speeds) / dt

    dx = calculate_dx(start_speeds, stop_speeds, dt)
    altitude_array=(np.tan(np.radians(slope_array))*dx).cumsum()

   

   # Find control stops
    cum_dtot = dx.cumsum() + cum_d * K
    print(cum_d)
    cum_dtot=cum_dtot / K
    cum_t = dt.cumsum() + DT_list_day[i]
    print(cum_t[:10])
    dfx=pd.DataFrame({'Cumulative Distance': cum_dtot, 'Time': cum_t})
    # l=str(i)
    # dfx.to_csv("xxxx"+l+".csv",index=False)
    control_stop_array =  find_control_stops((dfx))
    # control_stop_array = cum_t[np.searchsorted(cum_dtot, dis, side='right') for dis in d_control_stops]
    # control_stop_array=[i for i in control_stop_array if i!=0 or i!= len(cum_dtot)-1]
      
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

    energy_consumption = P_req * dt / HR # Wh

    #energy_consumption = energy_consumption.cumsum()
    energy_gain = P_solar['power'] * dt 

    energy_gain1 = energy_gain* HR
    energy_gain = energy_gain 
    
    #Add energy gained through control stop
    k=2*i
    for id, gt in enumerate(control_stop_array[range(0,len(indices))]):
        # print(id,indices[id])
        t = int((gt+k * CONTROL_STOP_DURATION) % (RunforDays * HR))
        
         # alpha,beta, _ = solar.Tilt_Angle(t + RACE_START, t + CONTROL_STOP_DURATION +  RACE_START, 232, lattitude_array[id], longitude_array[id], altitude_array[id])
        control_stop_E, _ =solar.Energy_Array_Racing(0,0, lattitude_array[id], longitude_array[id], altitude_array[id], np.array(range(t + RACE_START, t + CONTROL_STOP_DURATION +  RACE_START,STEP)), t + RACE_START, i, d=232)
        
        # print("en",energy_gain.cumsum()[indices[id]])
        # print("en",energy_gain.cumsum()[indices[id]+1])
        # print("en",energy_consumption.cumsum()[indices[id]])
        # print("en",energy_consumption.cumsum()[indices[id]+1])
        energy_gain[indices[id]] += control_stop_E
        # print("en1",energy_consumption.cumsum()[indices[id]])
        # print("en1",energy_consumption.cumsum()[indices[id]+1])
        # print("en1",energy_gain.cumsum()[indices[id]])
        # print("en1",energy_gain.cumsum()[indices[id]+1])
        k=k+1
    net_energy_profile = energy_consumption.cumsum() - energy_gain.cumsum()

    battery_profile = InitialBatteryCapacity - net_energy_profile
    battery_profile = np.concatenate((np.array([InitialBatteryCapacity]), battery_profile))

    battery_profile = battery_profile * 100 / (BATTERY_CAPACITY)
    #print("batt-less",battery_profile[indices])
    # print("bat_more",battery_profile[np.array(indices)])
    # print("bat_more1",battery_profile[np.array(indices)+1])
    # print("bat_more1",battery_profile[np.array(indices)+2])
    # Matching shapes
    dt =  np.concatenate((np.array([0]), dt))
    energy_gain = np.concatenate((np.array([np.nan]), energy_gain))
    #energy_gain = np.concatenate((np.array([np.nan]), energy_gain))
    energy_gain1 = np.concatenate((np.array([np.nan]), energy_gain1))
    energy_consumption =  np.concatenate((np.array([np.nan]), energy_consumption))
    acceleration = np.concatenate((np.array([np.nan]), acceleration,))
    dx = np.concatenate((np.array([0]), dx))
    
    return [
        dt.cumsum(),
        velocity_profile,
        acceleration,
        battery_profile,
        energy_consumption,
        energy_gain1 / HR,
        dx,
    ]