import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import numpy as np

# Page config
st.set_page_config(
    page_title="Ride Demand Predictor",
    page_icon="🚖",
    layout="wide"
)

# Custom CSS (modern dark UI)
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
h1 {
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("🚖 Smart Ride Demand & Pricing System")

# Sidebar
st.sidebar.header("🔧 Input Parameters")

hour = st.sidebar.slider("Hour of Day", 0, 23, 12)
day_of_week = st.sidebar.selectbox("Day of Week", list(range(7)))
is_weekend = 1 if day_of_week >= 5 else 0
temperature = st.sidebar.slider("Temperature (°C)", 20, 40, 28)
rain = st.sidebar.selectbox("Rain", [0, 1])
zone = st.sidebar.selectbox("Zone", [1, 2, 3, 4, 5])

# Derived features
is_peak_hour = 1 if (7 <= hour <= 10 or 17 <= hour <= 21) else 0
temp_level = 0 if temperature < 25 else (1 if temperature < 30 else 2)
rain_peak = rain * is_peak_hour

# Load model
model = joblib.load("model.pkl")

# Predict
if st.sidebar.button("🚀 Predict Demand"):

    input_data = pd.DataFrame({
        'hour': [hour],
        'day_of_week': [day_of_week],
        'is_weekend': [is_weekend],
        'temperature': [temperature],
        'rain': [rain],
        'zone': [zone],
        'is_peak_hour': [is_peak_hour],
        'temp_level': [temp_level],
        'rain_peak': [rain_peak]
    })

    prediction = model.predict(input_data)[0]

    # Pricing
    supply = 120
    surge = prediction / supply

    if surge < 1:
        multiplier = 1.0
    elif surge < 1.5:
        multiplier = 1.2
    else:
        multiplier = 1.5

    price = 100 * multiplier

    # KPI Cards
    col1, col2, col3 = st.columns(3)

    col1.metric("📊 Predicted Demand", int(prediction))
    col2.metric("⚡ Surge Multiplier", f"{surge:.2f}")
    col3.metric("💰 Ride Price (₹)", int(price))

    # Insight Messages
    if is_peak_hour:
        st.warning("🚨 Peak Hour Detected – High demand expected!")

    if rain:
        st.info("🌧 Rain detected – Demand likely to increase")

    # Generate sample time series data
    hours = np.arange(0, 24)
    demand_curve = [
        model.predict(pd.DataFrame({
            'hour': [h],
            'day_of_week': [day_of_week],
            'is_weekend': [is_weekend],
            'temperature': [temperature],
            'rain': [rain],
            'zone': [zone],
            'is_peak_hour': [1 if (7 <= h <= 10 or 17 <= h <= 21) else 0],
            'temp_level': [temp_level],
            'rain_peak': [rain * (1 if (7 <= h <= 10 or 17 <= h <= 21) else 0)]
        }))[0] for h in hours
    ]

    df_chart = pd.DataFrame({
        "Hour": hours,
        "Demand": demand_curve
    })

    # Plotly line chart
    fig = px.line(df_chart, x="Hour", y="Demand", title="📈 Demand Trend (24 Hours)")
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap data
    heatmap_data = np.random.randint(50, 200, size=(5, 24))

    fig2 = px.imshow(
        heatmap_data,
        labels=dict(x="Hour", y="Zone", color="Demand"),
        title="🔥 Demand Heatmap (Zone vs Hour)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.success("Prediction completed successfully!")