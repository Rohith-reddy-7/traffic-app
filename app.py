import streamlit as st
import pandas as pd
import pickle
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Smart City Traffic System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Title and header
st.title("🚗 Smart City Traffic Forecasting & Management System")
st.markdown("---")

# Load model and features
@st.cache_resource
def load_model():
    with open('models/traffic_model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model

@st.cache_resource
def load_features():
    with open('models/model_features.pkl', 'rb') as f:
        features = pickle.load(f)
    return features

# Alternate routes dictionary
alternate_routes = {
    1: "Gachibowli → Kondapur Road",
    2: "Hitech City → Madhapur Road",
    3: "Secunderabad → Begumpet Road",
    4: "Kukatpally → Moosapet Road"
}

# Junction names
junction_names = {
    1: "Gachibowli Junction",
    2: "Hitech City Junction",
    3: "Secunderabad Junction",
    4: "Kukatpally Junction"
}

def get_traffic_level(vehicles):
    """Determine traffic level based on vehicle count"""
    if vehicles < 150:
        return "Low", "🟢"
    elif vehicles < 350:
        return "Moderate", "🟡"
    elif vehicles < 500:
        return "Heavy", "🔴"
    else:
        return "Very Heavy", "🔴🔴"

def predict_traffic(junction_id, hour, day, month, weekday, is_weekend):
    """Predict traffic volume"""
    model = load_model()
    features = load_features()
    
    # Create input dataframe with same feature order
    input_data = pd.DataFrame({
        'junction_id': [junction_id],
        'hour': [hour],
        'day': [day],
        'month': [month],
        'weekday': [weekday],
        'is_weekend': [is_weekend]
    })
    
    # Ensure column order matches training
    input_data = input_data[features]
    
    # Make prediction
    prediction = model.predict(input_data)[0]
    return max(0, prediction)  # Ensure non-negative

# Sidebar inputs
st.sidebar.header("⚙️ Traffic Prediction Settings")

# Junction Selection
junction_id = st.sidebar.selectbox(
    "Select Junction / Area",
    options=[1, 2, 3, 4],
    format_func=lambda x: junction_names[x]
)

# Date Selection
selected_date = st.sidebar.date_input(
    "Select Date",
    value=datetime.now(),
    min_value=datetime(2024, 1, 1),
    max_value=datetime(2024, 12, 31)
)

# Time Selection
selected_time = st.sidebar.time_input(
    "Select Time",
    value=datetime.now().time()
)

# Calculate features
selected_datetime = datetime.combine(selected_date, selected_time)
hour = selected_datetime.hour
day = selected_datetime.day
month = selected_datetime.month
weekday = selected_datetime.weekday()
is_weekend = 1 if weekday >= 5 else 0

# Make prediction
predicted_vehicles = predict_traffic(junction_id, hour, day, month, weekday, is_weekend)
traffic_level, traffic_emoji = get_traffic_level(predicted_vehicles)

# Main content area - Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📍 Junction", junction_names[junction_id].split()[0])

with col2:
    st.metric("📅 Date", selected_date.strftime("%Y-%m-%d"))

with col3:
    st.metric("🕐 Time", selected_time.strftime("%H:%M"))

with col4:
    st.metric("🔍 Weekday", "Weekend" if is_weekend else "Weekday")

st.markdown("---")

# Prediction Results - High visibility
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🚗 Predicted Vehicle Count",
        f"{predicted_vehicles:.0f} vehicles",
        delta=None
    )

with col2:
    st.metric(
        "🚨 Traffic Level",
        f"{traffic_emoji} {traffic_level}",
        delta=None
    )

with col3:
    # Traffic indicator color
    if traffic_level == "Low":
        color = "🟢 Green"
    elif traffic_level == "Moderate":
        color = "🟡 Amber"
    else:
        color = "🔴 Red"
    st.metric("Signal Status", color)

st.markdown("---")

# Smart Traffic Management Alerts
st.header("⚠️ Smart Traffic Management")

if traffic_level in ["Heavy", "Very Heavy"]:
    alert_message = f"⚠️ **{traffic_level.upper()} TRAFFIC EXPECTED** at {junction_names[junction_id]} at {selected_time.strftime('%H:%M')}"
    st.warning(alert_message)
    
    # Show alternate route
    st.subheader("🗺️ Suggested Alternate Route")
    st.info(f"📍 {alternate_routes[junction_id]}")
else:
    st.success(f"✅ Traffic is {traffic_level.lower()} at {junction_names[junction_id]}. Regular route recommended.")

st.markdown("---")

# Public Transport Recommendations
st.header("🚌 Public Transport Planning")

if predicted_vehicles > 400:
    st.warning("High traffic predicted! Public transport recommendations:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Recommendations:
        - ✅ Increase metro frequency
        - ✅ Deploy additional buses
        - ✅ Extend public transit hours
        """)
    
    with col2:
        st.markdown("""
        ### 📈 Impact:
        - Reduce congestion by 15-20%
        - Improve average commute time
        - Lower transportation costs for commuters
        """)
else:
    st.info("✅ Normal traffic levels. Standard public transport schedule is sufficient.")

st.markdown("---")

# Visualizations
st.header("📊 Traffic Analytics & Visualizations")

# Load data for analytics
df = pd.read_csv('data/traffic.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df['hour'] = df['datetime'].dt.hour
df['day'] = df['datetime'].dt.day
df['month'] = df['datetime'].dt.month
df['weekday'] = df['datetime'].dt.weekday

# Tab for different visualizations
tab1, tab2, tab3 = st.tabs(["Hourly Traffic", "Traffic by Junction", "Peak Hour Analysis"])

# Tab 1: Hourly traffic prediction chart
with tab1:
    st.subheader("Hourly Traffic Prediction for Selected Junction")
    
    # Generate hourly predictions for the selected date
    hourly_data = []
    for h in range(24):
        pred = predict_traffic(junction_id, h, day, month, weekday, is_weekend)
        hourly_data.append({
            'Hour': f"{h:02d}:00",
            'Vehicles': pred
        })
    
    hourly_df = pd.DataFrame(hourly_data)
    
    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Scatter(
        x=hourly_df['Hour'],
        y=hourly_df['Vehicles'],
        mode='lines+markers',
        name='Predicted Vehicles',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    # Add traffic level zones as background
    fig_hourly.add_hrect(y0=0, y1=150, fillcolor="green", opacity=0.1, layer="below", name="Low")
    fig_hourly.add_hrect(y0=150, y1=350, fillcolor="yellow", opacity=0.1, layer="below", name="Moderate")
    fig_hourly.add_hrect(y0=350, y1=500, fillcolor="orange", opacity=0.1, layer="below", name="Heavy")
    fig_hourly.add_hrect(y0=500, y1=600, fillcolor="red", opacity=0.1, layer="below", name="Very Heavy")
    
    fig_hourly.update_layout(
        title=f"24-Hour Traffic Forecast for {junction_names[junction_id]}",
        xaxis_title="Time of Day",
        yaxis_title="Vehicle Count",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

# Tab 2: Traffic distribution by junction
with tab2:
    st.subheader("Traffic Distribution by Junction")
    
    junction_avg = df.groupby('junction_id')['vehicle_count'].agg(['mean', 'min', 'max']).reset_index()
    junction_avg['junction_name'] = junction_avg['junction_id'].map(junction_names)
    
    fig_junction = go.Figure()
    
    fig_junction.add_trace(go.Bar(
        x=junction_avg['junction_name'],
        y=junction_avg['mean'],
        name='Average Vehicles',
        marker_color='#636EFA'
    ))
    
    fig_junction.update_layout(
        title="Average Traffic Volume by Junction",
        xaxis_title="Junction",
        yaxis_title="Vehicle Count",
        height=400
    )
    st.plotly_chart(fig_junction, use_container_width=True)

# Tab 3: Peak hour analysis
with tab3:
    st.subheader("Peak Hour Analysis")
    
    peak_hours = df.groupby('hour')['vehicle_count'].mean().reset_index()
    
    fig_peak = go.Figure()
    fig_peak.add_trace(go.Bar(
        x=peak_hours['hour'],
        y=peak_hours['vehicle_count'],
        marker_color='#EF553B',
        name='Average Vehicles'
    ))
    
    fig_peak.update_layout(
        title="Average Traffic by Hour of Day",
        xaxis_title="Hour of Day",
        yaxis_title="Vehicle Count",
        xaxis={'dtick': 1},
        height=400
    )
    st.plotly_chart(fig_peak, use_container_width=True)

st.markdown("---")

# Footer
col1, col2, col3 = st.columns(3)
with col2:
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
    <p>🤖 Powered by XGBoost Machine Learning Model</p>
    <p>Last Updated: 2024 | Smart City Traffic Management</p>
    </div>
    """, unsafe_allow_html=True)
