from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import requests
from bs4 import BeautifulSoup
import random
app = Flask(__name__)

# Load the dataset once
data = pd.read_csv(r"C:\Users\Diksha\Desktop\rainfall dataset\district wise rainfall normal.csv")
def categorize_rainfall(amount):
    if amount <= 50:
        return "Low rainfall"
    elif 51 <= amount <= 150:
        return "Moderate rainfall"
    elif 151 <= amount <= 300:
        return "Heavy rainfall"
    elif 301 <= amount <= 500:
        return "Very heavy rainfall"
    else:
        return "Extremely heavy rainfall"

# Function to get district data
def get_district_data(state, district):
    district_data = data[(data['STATE_UT_NAME'] == state) & (data['DISTRICT'] == district)]
    if district_data.empty:
        return None
    rainfall_months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    monthly_rainfall = district_data[rainfall_months].values.flatten()
    avg_rainfall = district_data[rainfall_months].mean().values
    return pd.DataFrame({
        'Month': np.arange(1, 13),
        'Rainfall': monthly_rainfall,
        'AvgRainfall': avg_rainfall
    })

# Function to predict rainfall
def predict_future_rainfall(state, district, month):
    district_ts = get_district_data(state, district)
    if district_ts is None:
        return None, "Sorry, no data is available for the specified state and district."

    X = district_ts['Month'].values.reshape(-1, 1)
    y = district_ts['Rainfall'].values

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict rainfall for the selected month
    future_month_num = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5,
                        'JUN': 6, 'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 
                        'NOV': 11, 'DEC': 12}
    
    month_numeric = future_month_num.get(month.upper())
    if month_numeric is None:
        return None, "Invalid month. Please enter a valid month name."
    
    predicted_rainfall = model.predict(np.array([[month_numeric]]))[0]
    avg_rainfall = district_ts['AvgRainfall'][month_numeric - 1]
    
    # Prepare output
    rainfall_category = categorize_rainfall(predicted_rainfall)
    comparison = "above average" if predicted_rainfall > avg_rainfall else "below average" if predicted_rainfall < avg_rainfall else "on par with the average"
    
    return predicted_rainfall, f"Forecast for {month.upper()} in {district.title()}, {state.title()}:\n" \
                               f"- **Rainfall Amount**: {predicted_rainfall:.2f} mm ({rainfall_category})\n" \
                               f"- **Comparison to Average**: The expected rainfall is {comparison} compared to the historical average of {avg_rainfall:.2f} mm for {month.upper()}."

# Route for home page
@app.route('/')
def home():
    states = data['STATE_UT_NAME'].unique()
    return render_template('index.html', states=states)

# Route to get districts
@app.route('/get_districts', methods=['POST'])
def get_districts():
    state = request.json['state']
    districts = data[data['STATE_UT_NAME'] == state]['DISTRICT'].unique()
    return jsonify(districts.tolist())

# Route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    state = request.form['state']
    district = request.form['district']
    month = request.form['month']
    
    predicted_rainfall, result = predict_future_rainfall(state, district, month)
    
    if predicted_rainfall is None:
        return render_template('index.html', error=result, states=data['STATE_UT_NAME'].unique())
    
    return render_template('result.html', result=result)
@app.route('/weather', methods=['GET'])
def weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City name is required'}), 400
    
    weather_info = get_weather(city)
    return jsonify({'weather': weather_info})

# Function to get weather data
def get_weather(city):
    base_url = f'https://www.weather-forecast.com/locations/{city}/forecasts/latest'
    response = requests.get(base_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        weather_info = soup.find(class_='b-forecast__table-description-content').get_text(strip=True)
        return f"Weather in {city}: {weather_info}"
    else:
        return f"Error fetching weather data for {city}. Please check the city name and try again."
@app.route('/voice', methods=['GET'])
def voice():
    # Here, you would process voice input if needed
    # Currently returning a mock response
    return jsonify({'text': 'Mock state from voice input'})
if __name__ == '__main__':
    app.run(debug=True)
