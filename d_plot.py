import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from d_helper_fns import find_control_stops, find_reachtime
import d_config

# Custom CSS styles
custom_styles = {
    'font-family': '"Quicksand", sans-serif',
    'background-color': '#f0f0f0',
    'text-align': 'center',
    'margin': '10px',
    'padding': '10px',
    'border': '1px solid #ccc',
    'border-radius': '5px'
}
# Extra CSS style sheets
external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Quicksand:wght@300..700&family=Roboto+Slab:wght@100..900&family=Space+Grotesk:wght@300..700&display=swap",
]

# Initialize Dash app
def create_app(
        cum_dt, velocity_profile, acceleration_profile, battery_profile,
        energy_consumption_profile, solar_profile, cum_d, t_control_stops, t, v_avg
    ):
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        html.Div([
            html.Img(
                src='https://cfi.iitm.ac.in/assets/Agnirath-456b8655.png',
                style={
                    'height': '60px',
                    'margin-right': '10px',
                    'border': '1px solid #fe602c',
                    'border-radius': '50%',
                    'background-color': '#000000',
                }
            ),
            html.H1("Strategy Analysis Dashboard", style={'text-align': 'center', 'font-family': '"Roboto Slab", serif'}),
        ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center', 'align-items': 'center'}),
        
        html.Div([
            # Velocity profile plot
            dcc.Graph(
                id='velocity-profile',
                figure={
                    'data': [
                        go.Scatter(x=cum_dt, y=velocity_profile, mode='lines+markers', name='Velocity '),
                        go.Scatter(x=[min(cum_dt), max(cum_dt)], y=[d_config.MAX_V, d_config.MAX_V], mode='lines', name="Max Velocity", line=dict(color='red', dash='dot')),
                        go.Scatter(x=[9, 9], y=[0, d_config.MAX_V], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[18, 18], y=[0, d_config.MAX_V], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[27, 27], y=[0, d_config.MAX_V], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[36, 36], y=[0, d_config.MAX_V], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[45, 45], y=[0, d_config.MAX_V], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[t_control_stops[0], t_control_stops[0]], y=[0, d_config.MAX_V], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[1], t_control_stops[1]], y=[0, d_config.MAX_V], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[2], t_control_stops[2]], y=[0, d_config.MAX_V], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[3], t_control_stops[3]], y=[0, d_config.MAX_V], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[4], t_control_stops[4]], y=[0, d_config.MAX_V], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[5], t_control_stops[5]], y=[0, d_config.MAX_V], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[6], t_control_stops[6]], y=[0, d_config.MAX_V], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[7], t_control_stops[7]], y=[0, d_config.MAX_V], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[8], t_control_stops[8]], y=[0, d_config.MAX_V], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t, t], y=[0, d_config.MAX_V], mode='lines', name="Our Finish", line=dict(color='yellow', dash='dot')),

                    ],
                    'layout': go.Layout(title='Velocity Profile', xaxis={'title': 'Time (hr)'}, yaxis={'title': 'Velocity (m/s)'},
                                        shapes=[
                                            {
                                                'type': 'rect',
                                                'xref': 'x',
                                                'x0': t_control_stops[i],
                                                'x1': t_control_stops[i] + 0.5,
                                                'y0': 0,
                                                'y1': d_config.MAX_V,
                                                'fillcolor': 'LightSalmon',
                                                'opacity': 0.5,
                                                'line': {
                                                    'width': 0,
                                                },
                                            } for i in range(9)
                                        ])
                },
                style={'width': '93%', 'display': 'inline-block', 'vertical-align': 'top', **custom_styles}
            ),

            # Textual summary next to velocity profile
            html.Div([
                html.H2("Summary", style={'text-align': 'center', 'font-family': '"Space Grotesk", sans-serif'}),
                html.P(f"Total Distance: {round(cum_d[-1], 2)} km"),
                html.P(f"Time Taken: {(cum_dt[-1]*3600)//3600}hrs {((cum_dt[-1]*3600)%3600)//60}mins {round((((cum_dt[-1]*3600)%3600)%60), 3)}secs"),
                html.P(f"No of points: {len(cum_dt)}pts"),

            ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-left': '20px', **custom_styles}),
            
            # Textual summary next to velocity profile
            html.Div([
                html.H2("Data Analysis",
                        style={'text-align': 'center', 'font-family': '"Space Grotesk", sans-serif',
                               'margin-bottom': 0}),
                html.Div([
                    html.Div([
                        html.P(f"Max Velocity: {round(max(velocity_profile), 3)} m/s"),
                        html.P(f"Avg Velocity: {round(v_avg, 3)} m/s"),
                    ], style={'width': '50%'}),
                    html.Div([
                        html.P(f"Average Battery Level: {sum(battery_profile)/len(battery_profile):.2f}%")
                    ], style={'width': '50%'})
                ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'})
            ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-left': '20px', **custom_styles}),
        ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'}),

        # Grid layout for other profiles
        html.Div([
            dcc.Graph(
                id='acceleration-profile',
                figure={
                    'data': [go.Scatter(x=cum_dt[1:], y=acceleration_profile[1:], mode='lines+markers', name='Acceleration')],
                    'layout': go.Layout(title='Acceleration Profile', xaxis={'title': 'Time'}, yaxis={'title': 'Acceleration'})
                },
                style={'width': '45%', 'display': 'inline-block', **custom_styles}
            ),
            dcc.Graph(
                id='battery-profile',
                figure={
                    'data': [
                        go.Scatter(x=cum_dt, y=battery_profile, mode='lines+markers', name='Battery'),
                        go.Scatter(x=[min(cum_dt), max(cum_dt)], y=[100, 100], mode='lines', name="Max Battery Level", line=dict(color='red', dash='dot')),
                        go.Scatter(x=[min(cum_dt), max(cum_dt)], y=[d_config.DISCHARGE_CAP*100, d_config.DISCHARGE_CAP*100], mode='lines', name="Minimum battery Level", line=dict(color='orange', dash='dot')),
                        go.Scatter(x=[9, 9], y=[0, 100], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[18, 18], y=[0, 100], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[27, 27], y=[0, 100], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[36, 36], y=[0, 100], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[45, 45], y=[0, 100], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[t_control_stops[0], t_control_stops[0]], y=[0, 100], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[1], t_control_stops[1]], y=[0, 100], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[2], t_control_stops[2]], y=[0, 100], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[3], t_control_stops[3]], y=[0, 100], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[4], t_control_stops[4]], y=[0, 100], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[5], t_control_stops[5]], y=[0, 100], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[6], t_control_stops[6]], y=[0, 100], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[7], t_control_stops[7]], y=[0, 100], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[8], t_control_stops[8]], y=[0, 100], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t, t], y=[0, 100], mode='lines', name="Our Finish", line=dict(color='yellow', dash='dot')),

                    ],
                    'layout': go.Layout(title='Battery Profile', xaxis={'title': 'Time'}, yaxis={'title': 'Battery Level'},
                                        shapes=[
                                            {
                                                'type': 'rect',
                                                'xref': 'x',
                                                'x0': t_control_stops[i],
                                                'x1': t_control_stops[i] + 0.5,
                                                'y0': 0,
                                                'y1': 100,
                                                'fillcolor': 'LightSalmon',
                                                'opacity': 0.5,
                                                'line': {
                                                    'width': 0,
                                                },

                                            } for i in range(9)
                                        ])
                },
                style={'width': '45%', 'display': 'inline-block', **custom_styles}
            ),
            dcc.Graph(
                id='energy-consumption-profile',
                figure={
                    'data': [go.Scatter(x=cum_dt[1:], y=energy_consumption_profile[1:], mode='lines+markers', name='Energy Consumption')],
                    'layout': go.Layout(title='Energy Consumption Profile', xaxis={'title': 'Time'}, yaxis={'title': 'Energy Consumption'})
                },
                style={'width': '45%', 'display': 'inline-block', **custom_styles}
            ),
            dcc.Graph(
                id='solar-profile',
                figure={
                    'data': [go.Scatter(x=cum_dt[1:], y=solar_profile[1:], mode='lines+markers', name='Solar')],
                    'layout': go.Layout(title='Solar Profile', xaxis={'title': 'Time'}, yaxis={'title': 'Solar Energy'},
                                        shapes=[
                                            {
                                                'type': 'rect',
                                                'xref': 'x',
                                                'x0': t_control_stops[i],
                                                'x1': t_control_stops[i] + 0.5,
                                                'y0': 0,
                                                'y1': np.max(solar_profile),
                                                'fillcolor': 'LightSalmon',
                                                'opacity': 0.5,
                                                'line': {
                                                    'width': 0,
                                                },
                                            } for i in range(9)
                                        ])
                },
                style={'width': '45%', 'display': 'inline-block', **custom_styles}
            ),
            dcc.Graph(
                id='net-energy-consumption-profile',
                figure={
                    'data': [go.Scatter(x=cum_dt[1:], y=energy_consumption_profile[1:].cumsum(), mode='lines+markers', name='Energy Consumption')],
                    'layout': go.Layout(title='Net Energy Consumption Profile', xaxis={'title': 'Time'}, yaxis={'title': 'Energy Consumption'})
                },
                style={'width': '45%', 'display': 'inline-block', **custom_styles}
            ),
            dcc.Graph(
                id='net-solar-profile',
                figure={
                    'data': [go.Scatter(x=cum_dt[1:], y=solar_profile[1:].cumsum(), mode='lines+markers', name='Solar')],
                    'layout': go.Layout(title='Net Solar Profile', xaxis={'title': 'Time'}, yaxis={'title': 'Solar Energy'})
                },
                style={'width': '45%', 'display': 'inline-block', **custom_styles}
            ),
            dcc.Graph(
                id='dx-profile',
                figure={
                    'data': [
                        go.Scatter(x=cum_dt, y=cum_d, mode='lines+markers', name='Time'),
                        go.Scatter(x=[9, 9], y=[0, 3000], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[18, 18], y=[0, 3000], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[27, 27], y=[0, 3000], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[36, 36], y=[0, 3000], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[45, 45], y=[0, 3000], mode='lines', name="EndofDay", line=dict(color='green', dash='dot')),
                        go.Scatter(x=[t_control_stops[0], t_control_stops[0]], y=[0, 3000], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[1], t_control_stops[1]], y=[0, 3000], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[2], t_control_stops[2]], y=[0, 3000], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[3], t_control_stops[3]], y=[0, 3000], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[4], t_control_stops[4]], y=[0, 3000], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[5], t_control_stops[5]], y=[0, 3000], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[6], t_control_stops[6]], y=[0, 3000], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[7], t_control_stops[7]], y=[0, 3000], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t_control_stops[8], t_control_stops[8]], y=[0, 3000], mode='lines', name="ControlStop", line=dict(color='blue', dash='dot')),
                        go.Scatter(x=[t, t], y=[0, 3000], mode='lines', name="Our Finish", line=dict(color='yellow', dash='dot')),
          
                     ],
                    'layout': go.Layout(title='Distance Time Correlation', xaxis={'title': 'Time'}, yaxis={'title': 'Distance'})
                },
                style={'width': '45%', 'display': 'inline-block', **custom_styles}
            ),
        ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'})
    ], style={'background-color': '#ffffff', 'padding': '20px'})

    return app

if __name__ == '__main__':

    output = pd.read_csv("processed_run_dat.csv").fillna(0)

    cum_dt, velocity_profile, acceleration_profile, battery_profile, energy_consumption_profile, solar_profile, cum_d = map(np.array, (output[c] for c in output.columns.to_list()))

    run_dat = pd.read_csv("raw_run_dat.csv").fillna(0)
    v_avg = np.sum(np.array(run_dat['Velocity'])) / len(run_dat['Velocity'])
    #t_control_stops = find_control_stops(run_dat)
    
    t_end = find_reachtime(cum_dt, cum_d)
    print(t_end)

    app = create_app(
        cum_dt / 3600, velocity_profile, acceleration_profile, battery_profile,
        energy_consumption_profile, solar_profile, cum_d, find_control_stops(output)[range(0,len(find_control_stops(output)),10)]/3600, t_end / 3600, v_avg
    )
    print(find_control_stops(output)[range(0,len(find_control_stops(output)),10)]/3600)
    app.run_server(debug=True)