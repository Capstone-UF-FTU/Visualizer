import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import csv

#assuming 50MHz
frequency = 50 * 1_000_000
period = 1 / frequency

#will play the wave collected over 10 seconds
playback_time_seconds = 10

#callback interval
minimum_update_interval_milliseconds = 100

#total number of callbacks made to website
no_of_updates = (playback_time_seconds * 1000) / minimum_update_interval_milliseconds


results = []
#captured_data_points = Len of excel file

X = deque()
Y = deque()
counter = 0
old_clicks = 0

app = dash.Dash(__name__)
app.title = 'UF-FTU Visualizer'
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', 
                  animate=False,
                  ),
        dcc.Interval(
            id='graph-update',
            interval=1000
        ),
        html.Button('Replay Captured Sample', id='submit-val', n_clicks=0),
    ]
)


@app.callback(
            [Output('live-graph', 'figure'), Output('live-graph','animate'), Output('graph-update','disabled')],
            [Input("graph-update", "n_intervals"), Input('submit-val', 'n_clicks')]
            )
def update_graph_scatter(input_data, click):
    global counter
    global X
    global Y
    global old_clicks
        
    #reset waveform
    if old_clicks != click:
        X = deque()
        Y = deque()
        counter = 0
        old_clicks = click
        data = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(Y),
            name='Scatter',
            mode= 'lines+markers'
        )
        return [
                    {
                        'data': [data],
                        'layout' : go.Layout(
                                                xaxis=dict(range=[0,0], title="Time (Milliseconds)"), 
                                                yaxis=dict(range=[0,0], title="Measured Voltage (Millivolts)"),
                                                title="UF-FTU Captured Waveform",
                                                
                                            )
                    }, 
                    
                    False,
                    False,
                ]
        
    
    #if data points remain
    if counter < captured_data_points-1:
        counter += 1
        Y.append(results[counter][1])
        X.append(counter*100)

        data = plotly.graph_objs.Scatter(
                    x=list(X),
                    y=list(Y),
                    name='Scatter',
                    mode= 'lines+markers',
                )

        return [
                    {
                        'data': [data],
                        'layout' : go.Layout(
                                                xaxis=dict(range=[min(X),max(X)], title="Time (Milliseconds)"), 
                                                yaxis=dict(range=[min(Y),max(Y)], title="Measured Voltage (Millivolts)"),
                                                title="UF-FTU Captured Waveform",
                                                
                                            )
                    }, 
                    
                    False,
                    False,
                ]
    
    #else if all data points are exhausted
    else:
        data = plotly.graph_objs.Scatter(
                    x=list(X),
                    y=list(Y),
                    name='Scatter',
                    mode= 'lines+markers'
                )

        return [
                    {
                        'data': [data],
                        'layout' : go.Layout(
                                                xaxis=dict(range=[min(X),max(X)], title="Time (Milliseconds)"), 
                                                yaxis=dict(range=[min(Y),max(Y)], title="Measured Voltage (Millivolts)"),
                                                title="UF-FTU Captured Waveform",
                                                
                                            )
                    }, 
                    
                    False,
                    True,
                ]
        


if __name__ == '__main__':
    with open("input.csv") as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC) # change contents to floats
        for row in reader: # each row is a list
            results.append(row)

    captured_data_points = len(results)
    jump = captured_data_points / no_of_updates
    app.run_server(host='0.0.0.0', port=1200 ,debug=True)
