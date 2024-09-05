from d_offrace_solarcalc import calculate_energy
from d_solar import Solar
import pandas as pd
import numpy as np
from d_setting import RACE_START
dt = np.full(int(30), 200)
print('1')
df1 = pd.read_csv('locations_set.csv')
df2 = pd.read_csv('normals_set.csv')
df3 = pd.read_csv('areas_set.csv')
print('2')
df_buf = pd.concat([df1, df2, df3], axis=1)
print('3')
solar=Solar(df_buf)
print('4')
print(calculate_energy(RACE_START,RACE_START+6000)/3600)
print('5')
a,b=solar.Energy_Array_Racing(0,0, 0,0,30, dt, RACE_START, 0, 232)
print(a)
