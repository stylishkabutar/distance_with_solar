from d_helper_fns import format_data, add_control_stops
import pandas as pd

run_dat = pd.read_csv('raw_run_dat.csv')

processed_run_dat = format_data(run_dat)
processed_run_dat_1 = add_control_stops(processed_run_dat)

processed_run_dat_1.to_csv('processed_run_dat.csv', index = False)
# run_dat.to_csv('processed_run_dat.csv', index = False)