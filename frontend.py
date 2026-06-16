import streamlit as st
import requests

API_URL = "http://34.226.152.222:8000/predict"

st.title("Insurance Premium Category Predictor")
st.markdown("Enter your details below:")

age = st.number_input("Age", 1, 119, 30)
weight = st.number_input("Weight (kg)", 1.0, value=65.0)
height = st.number_input("Height (m)", 0.5, 2.5, 1.7)
income_lpa = st.number_input("Annual Income (LPA)", 0.1, value=10.0)
smoker = st.selectbox("Smoker", [True, False])
city = st.text_input("City", "Mumbai")
occupation = st.selectbox(
    "Occupation",
    ['retired', 'freelancer', 'student', 'government_job',
     'business_owner', 'unemployed', 'private_job']
)

if st.button("Predict"):
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(API_URL, json=input_data, timeout=10)
        result = response.json()

        if response.status_code == 200:
            prediction = result.get("response", result)

            st.success(f"Category: {prediction.get('predicted_category')}")
            st.write("Confidence:", prediction.get("confidence"))
            st.json(prediction.get("class_probabilities"))

        else:
            st.error(f"API Error {response.status_code}")
            st.json(result)

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")