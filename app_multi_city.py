"""
Enhanced Streamlit Dashboard - Multi-City Traffic Forecasting
Support for ANY metropolitan city with real-time predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from sklearn.preprocessing import LabelEncoder

# ═══════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="🚗 Smart Traffic Navigator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════
# CITY DATABASE
# ═══════════════════════════════════════════════════════════════════════

CITIES_DB = {
    "Hyderabad": {
        "center_lat": 17.3850,
        "center_lng": 78.4867,
        "junctions": {
            1: {"name": "Gachibowli", "lat": 17.3596, "lng": 78.3569},
            2: {"name": "Hitech City", "lat": 17.3614, "lng": 78.2422},
            3: {"name": "Secunderabad", "lat": 17.3711, "lng": 78.5019},
            4: {"name": "Kukatpally", "lat": 17.3844, "lng": 78.4181},
        }
    },
    "Mumbai": {
        "center_lat": 19.0760,
        "center_lng": 72.8777,
        "junctions": {
            1: {"name": "Bandra", "lat": 19.0596, "lng": 72.8295},
            2: {"name": "Dadar", "lat": 19.0176, "lng": 72.8479},
            3: {"name": "Andheri", "lat": 19.1136, "lng": 72.8697},
            4: {"name": "Virar", "lat": 19.4404, "lng": 72.7975},
        }
    },
    "Bangalore": {
        "center_lat": 12.9716,
        "center_lng": 77.5946,
        "junctions": {
            1: {"name": "Whitefield", "lat": 12.9698, "lng": 77.7499},
            2: {"name": "Koramangala", "lat": 12.9352, "lng": 77.6245},
            3: {"name": "Indiranagar", "lat": 12.9716, "lng": 77.6412},
            4: {"name": "MG Road", "lat": 12.9729, "lng": 77.6148},
        }
    },
    "Delhi": {
        "center_lat": 28.7041,
        "center_lng": 77.1025,
        "junctions": {
            1: {"name": "Connaught Place", "lat": 28.6329, "lng": 77.1879},
            2: {"name": "Gurgaon", "lat": 28.4595, "lng": 77.0266},
            3: {"name": "Noida", "lat": 28.5355, "lng": 77.3910},
            4: {"name": "Greater Noida", "lat": 28.4744, "lng": 77.5040},
        }
    },
    "Chennai": {
        "center_lat": 13.0827,
        "center_lng": 80.2707,
        "junctions": {
            1: {"name": "Anna Nagar", "lat": 13.0827, "lng": 80.2107},
            2: {"name": "Velachery", "lat": 12.9689, "lng": 80.2209},
            3: {"name": "Adyar", "lat": 13.0080, "lng": 80.2441},
            4: {"name": "Tambaram", "lat": 12.9191, "lng": 80.1670},
        }
    },
    "Pune": {
        "center_lat": 18.5204,
        "center_lng": 73.8567,
        "junctions": {
            1: {"name": "Hinjewadi", "lat": 18.5931, "lng": 73.7620},
            2: {"name": "Baner", "lat": 18.5596, "lng": 73.7997},
            3: {"name": "Viman Nagar", "lat": 18.5652, "lng": 73.9192},
            4: {"name": "Undri", "lat": 18.4681, "lng": 73.9239},
        }
    },
    "Kolkata": {
        "center_lat": 22.5726,
        "center_lng": 88.3639,
        "junctions": {
            1: {"name": "Saltlake", "lat": 22.5726, "lng": 88.4281},
            2: {"name": "Howrah", "lat": 22.5891, "lng": 88.2638},
            3: {"name": "New Market", "lat": 22.5467, "lng": 88.3685},
            4: {"name": "Ballygunge", "lat": 22.5187, "lng": 88.3776},
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════
# LOAD MODELS
# ═══════════════════════════════════════════════════════════════════════

@st.cache_resource
def load_model():
    """Load trained multi-city model"""
    try:
        with open('models/traffic_model_multicity.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        st.error("❌ Multi-city model not found. Run: python train_multi_city_model.py")
        return None

@st.cache_resource
def load_encoders_and_features():
    """Load encoders and feature columns"""
    try:
        with open('models/model_features_multicity.pkl', 'rb') as f:
            features = pickle.load(f)
        with open('models/city_encoder.pkl', 'rb') as f:
            city_encoder = pickle.load(f)
        with open('models/junction_encoder.pkl', 'rb') as f:
            junction_encoder = pickle.load(f)
        return features, city_encoder, junction_encoder
    except:
        return None, None, None

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def get_traffic_level(vehicles):
    """Classify traffic level based on vehicle count"""
    if vehicles < 100:
        return "🟢 Low", "#00CC00"
    elif vehicles < 250:
        return "🟡 Moderate", "#FFD700"
    elif vehicles < 400:
        return "🔴 Heavy", "#FF6347"
    else:
        return "🔴 Very Heavy", "#DC143C"

def predict_traffic(model, features, city_encoder, junction_encoder, city, junction_name, date, hour):
    """Make traffic prediction for given location and time"""
    try:
        # Encode city
        city_encoded = city_encoder.transform([city])[0]
        
        # Get junction ID from the junctions database
        city_info = CITIES_DB[city]
        junction_id = None
        for jid, jinfo in city_info['junctions'].items():
            if jinfo['name'] == junction_name:
                junction_id = jid
                break
        
        if junction_id is None:
            st.error("Junction not found")
            return None
        
        # Encode junction
        junction_key = f"{city}_{junction_id}"
        junction_encoded = junction_encoder.transform([junction_key])[0]
        
        # Extract date features
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day = date_obj.day
        month = date_obj.month
        weekday = date_obj.weekday()
        is_weekend = 1 if weekday >= 5 else 0
        
        # Create feature vector
        X = pd.DataFrame([[city_encoded, junction_encoded, hour, day, month, weekday, is_weekend]],
                         columns=features)
        
        # Predict
        prediction = model.predict(X)[0]
        return max(0, int(prediction))
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return None

def get_signal_status(vehicles):
    """Determine optimal traffic signal timing"""
    if vehicles < 100:
        return "🟢 Green: 30s", "Normal flow"
    elif vehicles < 250:
        return "🟡 Yellow: 20s", "Moderate congestion"
    elif vehicles < 400:
        return "🔴 Red: 90s", "Heavy congestion"
    else:
        return "🔴 Red: 120s", "Very heavy traffic"

def get_recommendations(vehicles, city, junction_name):
    """Get smart traffic recommendations"""
    recommendations = []
    
    if vehicles > 400:
        recommendations.append("⚠️ **Very Heavy Traffic** - Consider using public transport")
        recommendations.append("🚌 Buses/Metro available as alternative")
    elif vehicles > 250:
        recommendations.append("⚠️ **Heavy Traffic** - Expect delays")
        recommendations.append("💡 Consider flexible timings if possible")
    
    if junction_name in ["Gachibowli", "Hitech City"]:
        recommendations.append("🛣️ Alternate Route: Madhapur → Kondapur")
    elif junction_name in ["Andheri", "Bandra"]:
        recommendations.append("🛣️ Alternate Route: Via Linking Road")
    
    if vehicles > 300:
        recommendations.append("📱 Real-time updates: Use Google Maps for live traffic")
    
    return recommendations

# ═══════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════

def main():
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1>🌐 Smart City Traffic Navigator</h1>
        <h3>Real-Time Traffic Prediction for Indian Metropolitan Cities</h3>
        <p><i>Predict traffic patterns • Get smart recommendations • Optimize your commute</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load models
    model = load_model()
    features, city_encoder, junction_encoder = load_encoders_and_features()
    
    if model is None or features is None:
        st.error("❌ Models not loaded. Please train the model first.")
        st.code("python train_multi_city_model.py")
        return
    
    # ───────────────────────────────────────────────────────────────────
    # SIDEBAR: USER INPUTS
    # ───────────────────────────────────────────────────────────────────
    
    st.sidebar.markdown("## ⚙️ Traffic Forecast Settings")
    st.sidebar.divider()
    
    # City selection
    st.sidebar.markdown("### 📍 Select City")
    selected_city = st.sidebar.selectbox(
        "Choose a metropolitan city:",
        list(CITIES_DB.keys()),
        help="Select the city for traffic prediction"
    )
    
    city_info = CITIES_DB[selected_city]
    
    st.sidebar.markdown("### 🚗 Select Junction/Location")
    
    if selected_city in [k for k in CITIES_DB.keys()]:
        junctions = city_info['junctions']
        junction_options = list(junctions.values())
        junction_names = [j['name'] for j in junction_options]
        
        selected_junction_name = st.sidebar.selectbox(
            "Choose a junction:",
            junction_names,
            help="Select specific location in the city"
        )
    
    st.sidebar.markdown("### 📅 Select Date & Time")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        selected_date = st.date_input("Date:", datetime.now())
    with col2:
        selected_hour = st.slider("Hour (0-23):", 0, 23, 8)
    
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    
    st.sidebar.divider()
    st.sidebar.markdown("### 🎯 Available Cities")
    for i, city in enumerate(CITIES_DB.keys(), 1):
        st.sidebar.caption(f"{i}. {city}")
    
    # ───────────────────────────────────────────────────────────────────
    # PREDICTION & RESULTS
    # ───────────────────────────────────────────────────────────────────
    
    col1, col2, col3 = st.columns(3)
    
    # Make prediction
    predicted_vehicles = predict_traffic(
        model, features, city_encoder, junction_encoder,
        selected_city, selected_junction_name,
        selected_date_str, selected_hour
    )
    
    if predicted_vehicles is not None:
        traffic_level, color = get_traffic_level(predicted_vehicles)
        signal_status, signal_desc = get_signal_status(predicted_vehicles)
        
        with col1:
            st.metric(
                "🚗 Predicted Vehicles",
                f"{predicted_vehicles}",
                delta=None,
                delta_color="off"
            )
        
        with col2:
            st.markdown(f"<h4 style='color: {color}; text-align: center;'>{traffic_level}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'>{selected_junction_name}</p>", unsafe_allow_html=True)
        
        with col3:
            st.metric("🚦 Signal Status", signal_status.split(":")[0])
            st.caption(signal_desc)
        
        st.divider()
        
        # ───────────────────────────────────────────────────────────────
        # SMART RECOMMENDATIONS
        # ───────────────────────────────────────────────────────────────
        
        st.markdown("### 💡 Smart Traffic Recommendations")
        
        recommendations = get_recommendations(predicted_vehicles, selected_city, selected_junction_name)
        
        if recommendations:
            for rec in recommendations:
                st.info(rec)
        else:
            st.success("✅ Traffic flowing smoothly! No special recommendations.")
        
        st.divider()
        
        # ───────────────────────────────────────────────────────────────
        # TABS: VISUALIZATIONS & DETAILS
        # ───────────────────────────────────────────────────────────────
        
        tab1, tab2, tab3 = st.tabs(["📊 Hourly Forecast", "🗺️ City Overview", "📈 Traffic Analysis"])
        
        with tab1:
            st.markdown(f"#### Hourly Traffic Forecast - {selected_city} ({selected_junction_name})")
            
            hourly_data = []
            for h in range(24):
                pred = predict_traffic(
                    model, features, city_encoder, junction_encoder,
                    selected_city, selected_junction_name,
                    selected_date_str, h
                )
                hourly_data.append({"Hour": f"{h:02d}:00", "Vehicles": pred})
            
            hourly_df = pd.DataFrame(hourly_data)
            
            fig = px.line(
                hourly_df,
                x="Hour",
                y="Vehicles",
                markers=True,
                title=f"Traffic Pattern - {selected_city}",
                labels={"Vehicles": "Vehicle Count", "Hour": "Time of Day"},
                color_discrete_sequence=["#1f77b4"]
            )
            fig.update_layout(hovermode="x unified", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown(f"#### City Overview - {selected_city}")
            
            # Create comparison across all junctions
            junction_comparison = []
            for j_name in junction_names:
                pred = predict_traffic(
                    model, features, city_encoder, junction_encoder,
                    selected_city, j_name,
                    selected_date_str, selected_hour
                )
                level, _ = get_traffic_level(pred)
                junction_comparison.append({
                    "Junction": j_name,
                    "Vehicles": pred,
                    "Traffic Level": level
                })
            
            comp_df = pd.DataFrame(junction_comparison)
            
            fig = px.bar(
                comp_df,
                x="Junction",
                y="Vehicles",
                title=f"Traffic Comparison Across {selected_city} Junctions",
                color="Vehicles",
                color_continuous_scale="RdYlGn_r"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("#### Traffic Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Peak Hours**")
                peak_hours = []
                for h in range(24):
                    pred = predict_traffic(
                        model, features, city_encoder, junction_encoder,
                        selected_city, selected_junction_name,
                        selected_date_str, h
                    )
                    peak_hours.append({"Hour": h, "Vehicles": pred})
                
                peak_df = pd.DataFrame(peak_hours).nlargest(5, "Vehicles")
                st.dataframe(peak_df, use_container_width=True)
            
            with col2:
                st.markdown("**Off-Peak Hours**")
                off_peak_df = pd.DataFrame(peak_hours).nsmallest(5, "Vehicles")
                st.dataframe(off_peak_df, use_container_width=True)

if __name__ == "__main__":
    main()
