'''
Solar power calculation
'''
import numpy as np
import pandas as pd
from d_config import PANEL_AREA, PANEL_EFFICIENCY
from d_setting import RACE_START, DT
from scipy.spatial.transform import Rotation as R
from scipy.optimize import minimize
#send to config or setting
start_time = 8
del_T_utc = 9.5
start_day = 231
G0 = 1360
A = 6
rho = 0.01

def calc_solar_irradiance(time):
    '''
    Find Solar irradiance assuming Gausian distribution each day (temporary until solar data)
    '''
    return 1073.099 * np.exp(-0.5 * ((time - 43200) / 11600) ** 2)

def calculate_incident_solarpower(travel_time, latitude, longitude):
    '''
    Find instantanious solar power generated
    '''
    # gt = globaltime % DT # gives time spent on current day
    lt = RACE_START + travel_time # local time on current day
    intensity = calc_solar_irradiance(lt)
    return PANEL_AREA * PANEL_EFFICIENCY * intensity

class Solar:
    def __init__(self,car_df):
        self.car_df=car_df
    def HRA_calc(self,LT, d, Lo):
        B = 360 * (d - 81) / 365
        LSTM = 15 * del_T_utc
        EoT = 9.87 * np.sin(np.pi/180 * 2*B) - 7.53 * np.cos(np.pi/180 * B) - 1.5 * np.sin(np.pi/180 * B)
        TC = 4 * (Lo - LSTM) + EoT
        LST = np.array(LT) + TC/60
        HRA = 15 * (LST - 12)
        return HRA   
    def RT_Cartesian(self,cardinal_angle, elevation_angle, x_buf, y_buf, z_buf):
        cardinal_angle_r, elevation_angle_r = map(np.radians, (cardinal_angle, elevation_angle))
        rotation_x = R.from_euler('x', -elevation_angle_r)
        rotation_y = R.from_euler('y', -cardinal_angle_r)
        net_rotation = rotation_y * rotation_x      # first about x then about y
        x, y, z = net_rotation.apply(np.array([x_buf, y_buf, z_buf]).T).T
        return x, y, z
    def RT_Spherical(cardinal_angle, elevation_angle, beta, gamma):
     x_buf = - np.sin(np.radians(gamma)) * np.sin(np.radians(beta))
     y_buf = np.cos(np.radians(beta))
     z_buf = - np.cos(np.radians(gamma)) * np.sin(np.radians(beta))

     cardinal_angle_r, elevation_angle_r = map(np.radians, (cardinal_angle, elevation_angle))
     rotation_x = R.from_euler('x', -elevation_angle_r)
     rotation_y = R.from_euler('y', -cardinal_angle_r)
     net_rotation = rotation_y * rotation_x      # first about x then about y
    
     x, y, z = zip(*net_rotation.apply([x_buf, y_buf, z_buf]))
     beta_new = np.degrees(-np.arccos(y))
     gamma_new = np.degrees(np.arctan2(x, z))
     return beta_new, gamma_new
    def RT_Tilt(self,cardinal_angle, tilt, x_buf, y_buf, z_buf):
     cardinal_angle_r, tilt_r = map(np.radians, (cardinal_angle, tilt))
     rotation_x = R.from_euler('z', -tilt_r)
     rotation_y = R.from_euler('y', -cardinal_angle_r)
     net_rotation = rotation_y * rotation_x      # first about z then about y
     x, y, z = net_rotation.apply(np.array([x_buf, y_buf, z_buf]).T).T
     return x, y, z
    def Power_Panel(self,A, beta, gamma, LT, d, La, Lo, Alt):     # output: W

     Dec = -23.45 * np.cos(2*np.pi * (d + 10) / 365)
     HRA = self.HRA_calc(LT, d, Lo)
     A0 = 0.4237 - 0.00821*(6-Alt*0.001)**2
     A1 = 0.5055 - 0.00595*(0.5-Alt*0.001)**2
     k = 0.2711 + 0.01858*(2.5-Alt*0.001)**2
     
     Dec_r, beta_r, gamma_r, La_r, HRA_r = map(np.radians, (Dec, beta, gamma, La, HRA))
    #  print('len1',len(Dec_r))
 

     theta = np.arccos(np.sin(Dec_r)*np.sin(La_r)*np.cos(beta_r) - np.sin(Dec_r)*np.cos(La_r)*np.sin(beta_r)*np.cos(gamma_r) +
                      np.cos(Dec_r)*np.cos(La_r)*np.cos(beta_r)*np.cos(HRA_r) + np.cos(Dec_r)*np.sin(La_r)*np.sin(beta_r)*np.cos(gamma_r)*np.cos(HRA_r) +
                      np.cos(Dec_r)*np.sin(beta_r)*np.sin(gamma_r)*np.sin(HRA_r))
     
     thetaz = np.arccos(np.sin(Dec_r)*np.sin(La_r)*np.cos(0) - np.sin(Dec_r)*np.cos(La_r)*np.sin(0)*np.cos(0) +
                      np.cos(Dec_r)*np.cos(La_r)*np.cos(0)*np.cos(HRA_r) + np.cos(Dec_r)*np.sin(La_r)*np.sin(0)*np.cos(0)*np.cos(HRA_r) +
                      np.cos(Dec_r)*np.sin(0)*np.sin(0)*np.sin(HRA_r))
    
     Gb = G0 * (1 + 0.034 * np.cos(np.radians(360 * d / 365.25))) * (A0 + A1 * np.exp(-k / np.cos(thetaz)))
     Gd = G0 * (1 + 0.034 * np.cos(np.radians(360 * d / 365.25))) * np.cos(thetaz) * (0.2710 - 0.2931 * (A0 + A1 * np.exp(-k / np.cos(thetaz))))
     Gg = G0 * rho * ((1 - np.cos(np.radians(beta))) / 2)
     G = Gb * (np.cos(theta) / np.cos(thetaz)) + Gd * ((1 + np.cos(np.radians(beta))) / 2) + Gg

     power = G * A * np.cos(theta)
     return power
    def Energy_Panel(self, beta, gamma, df_pos):       # output: kWh
     df_pos_plus = df_pos.copy()
     time_diff = df_pos['time'].diff()
     df_pos_plus['time_diff'] = time_diff.fillna(0)
     df_pos_plus['local_time'] = 8 + ((df_pos['time'] / 3600) % 9)
     df_pos_plus['day'] = start_day + df_pos['time'] // (9*3600)

     df_pos_plus['beta_new'], df_pos_plus['gamma_new'] = self.RT_Spherical(df_pos_plus['cardinal_angle'], df_pos_plus['elevation_angle'], beta, gamma)
    def Power_Array_Standing(self,card_angle, tilt, LT, d, La, Lo, Alt):
     total_power = 0
     df_car=self.car_df
     x_buf, y_buf, z_buf, a = df_car['x_comp'], df_car['y_comp'], df_car['z_comp'], df_car['area']

     x, y, z = self.RT_Tilt(card_angle, tilt, x_buf, y_buf, z_buf)
     y = np.clip(y, -1, 1)

     a = a/1000000
     beta = np.degrees(-np.arccos(y))
     gamma = np.degrees(np.arctan2(x, z))
     total_power = self.Power_Panel(a, beta, gamma, LT, d, La, Lo, Alt).sum()

     return total_power 
    def Energy_Array_Standing(self,card_angle, tilt, LT_start, LT_stop, d, La, Lo, Alt):       # output: kWh
      N = 100                                         # Number of divisions of the time frame (try varying this)
      time_array = np.linspace(LT_start, LT_stop, N, endpoint=True)      # Verify if we need the last point (np.trapz)
      df_pow = pd.DataFrame()
      df_pow['time'] = time_array
      df_pow['power'] = df_pow.apply(lambda row: self.Power_Array_Standing(card_angle, tilt, row['time'], d, La, Lo, Alt), axis=1)
    # for t in time_array:
    #     df_pow['power'].append()
    #     # Take inspiration from below, maybe make time_array into a pandas dataframe and use .apply
    #     # df_pow['power'] = df_pos_plus.apply(lambda row: Power_Array(row['cardinal_angle'], row['elevation_angle'], row['local_time'], row['day'], row['latitude'], row['longitude'], row['altitude'], df_car), axis=1)
      energy = np.trapz(df_pow['power'], df_pow['time'])

      return energy/1000 

      energy = (df_pos_plus['time_diff'] * df_pos_plus.apply(lambda row: Power_Panel(A, row['beta_new'], row['gamma_new'], row['local_time'], row['day'], row['latitude'], row['longitude'], row['altitude']), axis=1)).sum()
      return energy/3600000
    def Tilt_Angle(LT_start, LT_stop, d, La, Lo, Alt, df_car):
      bounds = [(-180, 180), (0, 90)]
      initial_guess = [0, 0]
      result = minimize(lambda vars, LT_start, LT_stop, d, La, Lo, Alt, df_car : -self.Energy_Array_Standing(vars[0], vars[1], LT_start, LT_stop, d, La, Lo, Alt, df_car), \
                      initial_guess, args=(LT_start, LT_stop, d, La, Lo, Alt, df_car), bounds=bounds, method='L-BFGS-B')
    
      optimal_tilt, optimal_card_angle = result.x
      max_energy_output = -result.fun
      return optimal_tilt, optimal_card_angle
    def Power_Array_Racing(self,card_angle, ele_angle, LT, d, La, Lo, Alt):
     df_car=self.car_df
     x_buf, y_buf, z_buf, a = df_car['x_comp'], df_car['y_comp'], df_car['z_comp'], df_car['area']

     x, y, z = self.RT_Cartesian( card_angle, ele_angle, x_buf, y_buf, z_buf)
     y = np.clip(y, -1, 1)

     a = a/1000000                                           # Converting mm^2 to m^2
     beta = np.degrees(-np.arccos(y))
     gamma = np.degrees(np.arctan2(x, z))
     total_power = self.Power_Panel(a, beta, gamma, LT, d, La, Lo, Alt).sum()

     return total_power 
    def Energy_Array_Racing(self, card_angle, elevation_angle, latitude, longitude, altitude,  dt, start_time, i, d=232):       # output: kWh
     df_pos_plus=pd.DataFrame()
     time_diff = dt 
     df_pos_plus['time_diff'] = time_diff
     df_pos_plus['local_time'] = (start_time + dt.cumsum())/3600
     df_pos_plus['day'] = d+i 
     df_pos_plus['card_angle']=np.full(len(df_pos_plus['day']), card_angle)
     df_pos_plus['elevation_angle']=np.full(len(df_pos_plus['day']), elevation_angle)
     df_pos_plus['latitude']=np.full(len(df_pos_plus['day']), latitude)
     df_pos_plus["longitude"]=np.full(len(df_pos_plus['day']), longitude)
     df_pos_plus['altitude']=np.full(len(df_pos_plus['day']), altitude)

     df_pow = pd.DataFrame()
     df_pow['time'] = dt.cumsum()
     df_pow['power'] = df_pos_plus.apply(lambda row: self.Power_Array_Racing(row["card_angle"],row['elevation_angle'], row['local_time'], row['day'], row['latitude'], row['longitude'], row['altitude']), axis=1)
     
     energy = np.trapz(df_pow['power'], df_pow['time'])

     return energy/3600000, df_pow
    def Tilt_Angle(self,LT_start, LT_stop, d, La, Lo, Alt):
     car_df=self.car_df
     bounds = [(-180, 180), (0, 90)]
     initial_guess = [0, 0]
     result = minimize(lambda vars, LT_start, LT_stop, d, La, Lo, Alt : -self.Energy_Array_Standing(vars[0], vars[1], LT_start, LT_stop, d, La, Lo, Alt), \
                      initial_guess, args=(LT_start, LT_stop, d, La, Lo, Alt), bounds=bounds, method='L-BFGS-B')
    
     optimal_tilt, optimal_card_angle = result.x
     max_energy_output = -result.fun
     return  optimal_card_angle, optimal_tilt, max_energy_output