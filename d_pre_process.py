from d_helper_fns import set_at_sampling_rate
import pandas as pd

route_df = pd.read_csv('raw_route_data_final.csv')

set_at_sampling_rate(route_df)