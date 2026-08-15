import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import paho.mqtt.client as mqtt
import json
from collections import deque
import datetime

# ======== DATA STORAGE ========
temp_data = deque(maxlen=30)
humid_data = deque(maxlen=30)
light_data = deque(maxlen=30)
dist_data = deque(maxlen=30)
time_data = deque(maxlen=30)

# ======== MQTT SUBSCRIBER ========
def on_connect(client, userdata, flags, rc):
    print("✅ Connected to MQTT Broker")
    client.subscribe("esp32/sensors")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        temp_data.append(payload.get("temperature", 0))
        humid_data.append(payload.get("humidity", 0))
        light_data.append(payload.get("ldr", 0))
        dist_data.append(payload.get("distance", 0))
        time_data.append(datetime.datetime.now().strftime("%H:%M:%S"))
        print(f"📥 Received: {payload}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("10.232.107.137", 1883, 60)
mqtt_client.loop_start()

# ======== CREATE DASH APP ========
app = dash.Dash(__name__)
app.title = "Group μ - IoT Control Center"

# ======== DASH LAYOUT ========
app.layout = html.Div(
    style={'backgroundColor': '#0d1117', 'color': '#c9d1d9', 'padding': '20px', 'minHeight': '100vh', 'fontFamily': 'Arial, sans-serif'},
    children=[

        # ---- TITLE ----
        html.H1("⚡ GROUP μ - ADVANCED IoT CONTROL CENTER", 
                style={'textAlign': 'center', 'color': '#58a6ff', 'fontSize': '28px', 'marginBottom': '5px'}),
        html.Hr(style={'borderColor': '#30363d', 'marginBottom': '15px'}),

        # ==========================================
        # ROW 1: 4 GAUGES (TITLES FULLY VISIBLE!)
        # ==========================================
        html.Div([
            html.Div(dcc.Graph(id='temp-gauge', config={'displayModeBar': False}), 
                    style={'width': '23%', 'display': 'inline-block', 'padding': '0px'}),
            html.Div(dcc.Graph(id='humid-gauge', config={'displayModeBar': False}), 
                    style={'width': '23%', 'display': 'inline-block', 'padding': '0px'}),
            html.Div(dcc.Graph(id='light-gauge', config={'displayModeBar': False}), 
                    style={'width': '23%', 'display': 'inline-block', 'padding': '0px'}),
            html.Div(dcc.Graph(id='dist-gauge', config={'displayModeBar': False}), 
                    style={'width': '23%', 'display': 'inline-block', 'padding': '0px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 'marginBottom': '10px'}),

        # ==========================================
        # ROW 2: LIGHT & DISTANCE PANELS
        # ==========================================
        html.Div([
            # ---- LIGHT PANEL ----
            html.Div([
                html.H4("☀️ LIGHT INTENSITY", style={'color': '#f0883e', 'textAlign': 'center', 'margin': '5px 0px'}),
                html.Div(
                    id='light-bar-container', 
                    style={
                        'height': '30px', 
                        'backgroundColor': '#30363d', 
                        'borderRadius': '20px', 
                        'overflow': 'hidden', 
                        'border': '2px solid #30363d',
                        'position': 'relative'
                    },
                    children=[
                        html.Div(
                            id='light-bar-fill', 
                            style={
                                'height': '100%', 
                                'width': '0%', 
                                'borderRadius': '20px', 
                                'transition': 'width 0.5s ease', 
                                'backgroundColor': '#ffdd00',
                                'position': 'absolute',
                                'top': '0',
                                'left': '0'
                            }
                        )
                    ]
                ),
                html.Div(id='light-status-text', style={'marginTop': '5px', 'fontSize': '18px', 'textAlign': 'center', 'fontWeight': 'bold'})
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 'backgroundColor': '#161b22', 'borderRadius': '15px', 'verticalAlign': 'top'}),
            
            # ---- DISTANCE PANEL ----
            html.Div([
                html.H4("📏 PROXIMITY RULER", style={'color': '#3fb950', 'textAlign': 'center', 'margin': '5px 0px'}),
                html.Div(
                    id='dist-bar-container', 
                    style={
                        'height': '30px', 
                        'backgroundColor': '#30363d', 
                        'borderRadius': '20px', 
                        'overflow': 'hidden', 
                        'border': '2px solid #30363d',
                        'position': 'relative'
                    },
                    children=[
                        html.Div(
                            id='dist-bar-fill', 
                            style={
                                'height': '100%', 
                                'width': '0%', 
                                'borderRadius': '20px', 
                                'transition': 'width 0.5s ease', 
                                'backgroundColor': '#3fb950',
                                'position': 'absolute',
                                'top': '0',
                                'left': '0'
                            }
                        )
                    ]
                ),
                html.Div(id='dist-status-text', style={'marginTop': '5px', 'fontSize': '18px', 'textAlign': 'center', 'fontWeight': 'bold'})
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 'backgroundColor': '#161b22', 'borderRadius': '15px', 'verticalAlign': 'top'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}),

        # ==========================================
        # ROW 3: ALERT BOX
        # ==========================================
        html.Div(id='alert-box', style={'padding': '15px', 'borderRadius': '15px', 'margin': '10px 0px', 'fontWeight': 'bold', 'fontSize': '22px', 'textAlign': 'center', 'border': '2px solid #30363d'}),

        dcc.Interval(id='interval', interval=2000),

        # ==========================================
        # ROW 4: GRAPHS
        # ==========================================
        html.Div([
            html.Div(dcc.Graph(id='temp-graph', style={'height': '250px'}), style={'width': '48%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(id='humid-graph', style={'height': '250px'}), style={'width': '48%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}),
        
        html.Div([
            html.Div(dcc.Graph(id='light-graph', style={'height': '250px'}), style={'width': '48%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(id='dist-graph', style={'height': '250px'}), style={'width': '48%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ]
)

# ============================================================
# 📊 CALLBACKS: UPDATE GAUGES (TITLES FULLY VISIBLE!)
# ============================================================

@app.callback(Output('temp-gauge', 'figure'), Input('interval', 'n_intervals'))
def update_temp_gauge(n):
    val = temp_data[-1] if temp_data else 0
    return go.Figure(go.Indicator(
        mode="gauge+number", 
        value=val, 
        title={'text': "🌡️ Temperature (°C)", 'font': {'size': 13}},
        gauge={
            'axis': {'range': [0, 40], 'tickwidth': 1, 'tickcolor': "white"}, 
            'bar': {'color': "#ff7b72"}, 
            'bgcolor': 'rgba(0,0,0,0)'
        }
    )).update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color='white', 
        height=150,  # <--- INCREASED FOR FULL VISIBILITY!
        margin=dict(l=5, r=5, t=45, b=5)  # <--- MORE TOP SPACE!
    )

@app.callback(Output('humid-gauge', 'figure'), Input('interval', 'n_intervals'))
def update_humid_gauge(n):
    val = humid_data[-1] if humid_data else 0
    return go.Figure(go.Indicator(
        mode="gauge+number", 
        value=val, 
        title={'text': "💧 Humidity (%)", 'font': {'size': 13}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"}, 
            'bar': {'color': "#58a6ff"}, 
            'bgcolor': 'rgba(0,0,0,0)'
        }
    )).update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color='white', 
        height=150,  # <--- INCREASED FOR FULL VISIBILITY!
        margin=dict(l=5, r=5, t=45, b=5)  # <--- MORE TOP SPACE!
    )

@app.callback(Output('light-gauge', 'figure'), Input('interval', 'n_intervals'))
def update_light_gauge(n):
    val = light_data[-1] if light_data else 0
    return go.Figure(go.Indicator(
        mode="gauge+number", 
        value=val, 
        title={'text': "☀️ Light Intensity (%)", 'font': {'size': 13}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"}, 
            'bar': {'color': "#f0883e"}, 
            'bgcolor': 'rgba(0,0,0,0)'
        }
    )).update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color='white', 
        height=150,  # <--- INCREASED FOR FULL VISIBILITY!
        margin=dict(l=5, r=5, t=45, b=5)  # <--- MORE TOP SPACE!
    )

@app.callback(Output('dist-gauge', 'figure'), Input('interval', 'n_intervals'))
def update_dist_gauge(n):
    val = dist_data[-1] if dist_data else 0
    return go.Figure(go.Indicator(
        mode="gauge+number", 
        value=val, 
        title={'text': "📏 Distance (cm)", 'font': {'size': 13}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"}, 
            'bar': {'color': "#3fb950"}, 
            'bgcolor': 'rgba(0,0,0,0)'
        }
    )).update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color='white', 
        height=150,  # <--- INCREASED FOR FULL VISIBILITY!
        margin=dict(l=5, r=5, t=45, b=5)  # <--- MORE TOP SPACE!
    )

# ============================================================
# 🔔 CALLBACK: SMART ALERT BOX
# ============================================================
@app.callback(
    Output('alert-box', 'children'),
    Output('alert-box', 'style'),
    Input('interval', 'n_intervals')
)
def update_alerts(n):
    if not temp_data:
        return "⏳ Waiting for ESP32 Data...", {'backgroundColor': '#21262d', 'color': '#8b949e', 'padding': '15px', 'borderRadius': '15px', 'textAlign': 'center', 'border': '2px solid #30363d', 'fontSize': '22px'}
    
    temp = temp_data[-1]
    dist = dist_data[-1]
    light = light_data[-1] if light_data else 100

    if temp > 35:
        return "🔥 CRITICAL: Overheating! (>35°C)", {'backgroundColor': '#da3633', 'color': 'white', 'padding': '15px', 'borderRadius': '15px', 'textAlign': 'center', 'border': '3px solid red', 'fontSize': '22px'}
    elif 0 < dist < 10:
        return "🚨 DANGER: Object too close! (<10cm)", {'backgroundColor': '#da3633', 'color': 'white', 'padding': '15px', 'borderRadius': '15px', 'textAlign': 'center', 'border': '3px solid orange', 'fontSize': '22px'}
    elif temp > 30:
        return "⚠️ WARNING: High Temperature", {'backgroundColor': '#d29922', 'color': 'black', 'padding': '15px', 'borderRadius': '15px', 'textAlign': 'center', 'border': '2px solid #ffaa00', 'fontSize': '22px'}
    elif light < 20:
        return "🌙 Dark Mode Detected (Low Light)", {'backgroundColor': '#1f2937', 'color': '#58a6ff', 'padding': '15px', 'borderRadius': '15px', 'textAlign': 'center', 'border': '2px solid #58a6ff', 'fontSize': '22px'}
    else:
        return "✅ SYSTEM NORMAL - All readings stable", {'backgroundColor': '#238636', 'color': 'white', 'padding': '15px', 'borderRadius': '15px', 'textAlign': 'center', 'border': '2px solid #2ea043', 'fontSize': '22px'}

# ============================================================
# 🆕 CALLBACKS: ENHANCED LIGHT & DISTANCE PANELS
# ============================================================

@app.callback(
    Output('light-bar-fill', 'style'),
    Output('light-status-text', 'children'),
    Input('interval', 'n_intervals')
)
def update_light_panel(n):
    if not light_data:
        return {'width': '0%', 'backgroundColor': '#30363d', 'position': 'absolute', 'top': '0', 'left': '0'}, "⏳ Waiting..."
    
    val = light_data[-1]
    bar_style = {
        'height': '100%', 
        'width': f'{val}%', 
        'borderRadius': '20px', 
        'transition': 'width 0.5s ease',
        'position': 'absolute',
        'top': '0',
        'left': '0'
    }
    
    if val > 70:
        bar_style['backgroundColor'] = '#ffdd00'
        status = f"☀️ Sunny ({val}%)"
    elif val > 40:
        bar_style['backgroundColor'] = '#f0883e'
        status = f"⛅ Cloudy ({val}%)"
    elif val > 15:
        bar_style['backgroundColor'] = '#8b949e'
        status = f"🌆 Dusk ({val}%)"
    else:
        bar_style['backgroundColor'] = '#1f2937'
        status = f"🌙 Dark ({val}%)"
    
    return bar_style, status

@app.callback(
    Output('dist-bar-fill', 'style'),
    Output('dist-status-text', 'children'),
    Input('interval', 'n_intervals')
)
def update_distance_panel(n):
    if not dist_data:
        return {'width': '0%', 'backgroundColor': '#30363d', 'position': 'absolute', 'top': '0', 'left': '0'}, "⏳ Waiting..."
    
    val = dist_data[-1]
    bar_width = min(val, 100)
    bar_style = {
        'height': '100%', 
        'width': f'{bar_width}%', 
        'borderRadius': '20px', 
        'transition': 'width 0.5s ease',
        'position': 'absolute',
        'top': '0',
        'left': '0'
    }
    
    if val < 10 and val > 0:
        bar_style['backgroundColor'] = '#da3633'
        status = f"🔴 DANGER: Object too close! ({val:.1f}cm)"
    elif val < 20:
        bar_style['backgroundColor'] = '#d29922'
        status = f"🟠 WARNING: Getting close ({val:.1f}cm)"
    elif val == 0:
        bar_style['backgroundColor'] = '#8b949e'
        status = f"📡 No object detected"
    else:
        bar_style['backgroundColor'] = '#3fb950'
        status = f"✅ Clear ({val:.1f}cm)"
    
    return bar_style, status

# ============================================================
# 📈 CALLBACKS: UPDATE GRAPHS
# ============================================================
@app.callback(Output('temp-graph', 'figure'), Input('interval', 'n_intervals'))
def update_temp_graph(n):
    return go.Figure(data=[go.Scatter(x=list(time_data), y=list(temp_data), mode='lines+markers', line=dict(color='#ff7b72'))]).update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=10, t=30, b=30), xaxis_title='Time', yaxis_title='°C', height=250)

@app.callback(Output('humid-graph', 'figure'), Input('interval', 'n_intervals'))
def update_humid_graph(n):
    return go.Figure(data=[go.Scatter(x=list(time_data), y=list(humid_data), mode='lines+markers', line=dict(color='#58a6ff'))]).update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=10, t=30, b=30), xaxis_title='Time', yaxis_title='%', height=250)

@app.callback(Output('light-graph', 'figure'), Input('interval', 'n_intervals'))
def update_light_graph(n):
    return go.Figure(data=[go.Scatter(x=list(time_data), y=list(light_data), mode='lines+markers', line=dict(color='#f0883e'))]).update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=10, t=30, b=30), xaxis_title='Time', yaxis_title='%', height=250)

@app.callback(Output('dist-graph', 'figure'), Input('interval', 'n_intervals'))
def update_dist_graph(n):
    return go.Figure(data=[go.Scatter(x=list(time_data), y=list(dist_data), mode='lines+markers', line=dict(color='#3fb950'))]).update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=10, t=30, b=30), xaxis_title='Time', yaxis_title='cm', height=250)

# ============================================================
# 🚀 RUN THE APP
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, port=8050)
