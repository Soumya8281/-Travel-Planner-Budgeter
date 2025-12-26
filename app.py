import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# ------------------- Page Config -------------------
st.set_page_config(page_title="Travel Planner", layout="wide")
st.title("🧳 Travel Planner & Budgeter")

# ------------------- User Inputs -------------------
st.markdown("### ✈️ Enter Your Travel Details")

destination = st.text_input("🌍 Destination (e.g., Paris, New York, India):").strip()
num_days = st.number_input("📅 Number of days:", 1, 30, 3)
num_travelers = st.number_input("👥 Number of travelers:", 1, 10, 1)

st.divider()
st.markdown("### 💰 Budget Details")

col1, col2, col3 = st.columns(3)
with col1:
    daily_food_cost = st.number_input("🍽️ Food cost per day ($):", 0, 1000, 30)
with col2:
    hotel_cost_per_night = st.number_input("🏨 Hotel cost per night ($):", 0, 2000, 50)
with col3:
    transport_mode = st.selectbox("🚗 Transport mode:", ["Flight", "Train", "Bus", "Car"])
    transport_cost_dict = {"Flight": 200, "Train": 100, "Bus": 50, "Car": 150}
    transport_cost = transport_cost_dict[transport_mode]

# ------------------- Hotel Recommendations -------------------
st.divider()
st.markdown("### 🏠 Hotel Recommendations")

hotel_type = st.radio("Select hotel type:", ["Budget", "Mid-range", "Luxury"], horizontal=True)
hotel_price_dict = {"Budget": 40, "Mid-range": 80, "Luxury": 150}
recommended_hotel_price = hotel_price_dict[hotel_type]
st.info(f"Recommended hotel cost per night for {hotel_type}: **${recommended_hotel_price}**")

use_recommended = st.checkbox("✅ Use recommended hotel price", value=True)
if use_recommended:
    hotel_cost_per_night = recommended_hotel_price

# ------------------- Budget Calculation -------------------
def calculate_budget(hotel, food, transport, days, travelers):
    total_hotel = hotel * days * travelers
    total_food = food * days * travelers
    total_transport = transport * travelers 
    total_budget = total_hotel + total_food + total_transport
    return total_budget, total_hotel, total_food, total_transport

# ------------------- budget calculation -------------------
if st.button("💵 Calculate Budget"):
    if not destination:
        st.error("⚠️ Please enter a destination before proceeding!")
    else:
        total, hotel_total, food_total, transport_total = calculate_budget(
            hotel_cost_per_night, daily_food_cost, transport_cost, num_days, num_travelers
        )

        # ----- Trip Summary -----
        st.divider()
        st.markdown("## 📝 Trip Summary")
        st.write(f"**Destination:** {destination.title()}")
        st.write(f"**Days:** {num_days} | **Travelers:** {num_travelers}")
        st.write(f"**Transport:** {transport_mode}")
        st.write(f"**Hotel Type:** {hotel_type}")
        st.success(f"**Total Budget:** ${total} (Per Traveler: ${total/num_travelers:.2f})")

        # ----- Budget Breakdown -----
        st.divider()
        st.markdown("## 💰 Budget Breakdown")
        budget_df = pd.DataFrame({
            "Category": ["Hotel", "Food", "Transport"],
            "Cost": [hotel_total, food_total, transport_total]  
        })
        st.bar_chart(budget_df.set_index("Category"))

        
      

        # ----- Travel Tips -----
        st.divider()
        st.markdown("## 🌍 Travel Tips")
        tips_dict = {
            "Paris": "Best to visit in spring or fall. Pack comfortable shoes for walking.",
            "Switzerland": "Carry warm clothes. Train travel is convenient and scenic.",
            "Maldives": "Visit during dry season. Sun protection is essential.",
            "New York": "Check traffic times and plan sightseeing in advance.",
            "India": "Best to visit between October and March. Carry light cotton clothes for summer and warm clothes for winter in northern regions.",
            "Default": "Check local weather, currency, and travel guidelines before travel."
        }
        tip = tips_dict.get(destination.title(), tips_dict["Default"])
        st.info(tip)

        # ----- Weather Info -----
        st.divider()
        st.markdown("## 🌤 Current Weather")
        try:
            headers = {"User-Agent": "TravelPlannerApp/1.0"}
            geo_resp = requests.get(
                f"https://nominatim.openstreetmap.org/search?q={destination}&format=json",
                headers=headers
            ).json()
            if geo_resp:
                lat = geo_resp[0]["lat"]
                lon = geo_resp[0]["lon"]
                weather_resp = requests.get(
                    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                ).json()
                current = weather_resp["current_weather"]
                st.write(f"**City:** {destination.title()}")
                st.write(f"**Temperature:** {current['temperature']} °C")
                st.write(f"**Wind Speed:** {current['windspeed']} m/s")
            else:
                st.warning("City not found. Please check spelling.")
        except Exception as e:
            st.warning(f"Could not fetch weather data. Error: {e}")

        # ----- Activities -----
        st.divider()
        st.markdown("## 🤖 Recommended Activities")
        user_type = st.radio("Trip Type:", ["Adventure", "Relaxation", "Sightseeing"], horizontal=True)
        activities = {
            "Adventure": ["Hiking", "Rafting", "Paragliding"],
            "Relaxation": ["Spa", "Beach", "Yoga"],
            "Sightseeing": ["Museum", "City Tour", "Historic Sites"]
        }
        st.write("**Suggestions:**", ", ".join(activities[user_type]))

        # ----- Currency -----  
        st.divider()
        st.markdown("## 💱 Currency Conversion")
        try:
            response_currency = requests.get("https://api.frankfurter.app/latest?from=USD&to=EUR,INR").json()
            eur_rate = response_currency['rates']['EUR']
            inr_rate = response_currency['rates']['INR']
            st.write(f"1 USD = {eur_rate} EUR")
            st.write(f"1 USD = {inr_rate} INR")
            
            if destination.title() == "India":
                st.info("Currency for India: INR (Indian Rupee)")
        except:
            st.warning("Currency API not available.")
