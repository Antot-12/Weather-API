from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__, template_folder='templates')
CORS(app)

# Ваш API ключ OpenWeatherMap
API_KEY = 'ecbe514c3a3b657e300a75d24305c3b5'

# Базовий URL для запитів до OpenWeatherMap API
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    units = request.args.get('units', 'metric')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not city and not (lat and lon):
        return jsonify({'error': 'Either city or coordinates (lat, lon) must be provided.'}), 400

    params = {
        'appid': API_KEY,
        'units': units,
    }

    if city:
        params['q'] = city
    else:
        params['lat'] = lat
        params['lon'] = lon

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        return jsonify({'error': 'City not found or API request failed. Please check the provided parameters.'}), 404

    data = response.json()

    if 'name' not in data or 'main' not in data:
        return jsonify({'error': 'Invalid response from weather API. Please try again later.'}), 500

    weather_data = {
        'city': data.get('name'),
        'temperature': data['main'].get('temp'),
        'description': data['weather'][0].get('description') if data['weather'] else 'No description available',
        'humidity': data['main'].get('humidity'),
        'wind_speed': data['wind'].get('speed'),
        'units': 'metric' if units == 'metric' else 'imperial'
    }

    return jsonify(weather_data)


@app.route('/forecast', methods=['GET'])
def get_forecast():
    city = request.args.get('city')
    units = request.args.get('units', 'metric')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not city and not (lat and lon):
        return jsonify({'error': 'Either city or coordinates (lat, lon) must be provided.'}), 400

    params = {
        'appid': API_KEY,
        'units': units,
    }

    if city:
        params['q'] = city
    else:
        params['lat'] = lat
        params['lon'] = lon

    response = requests.get(FORECAST_URL, params=params)

    if response.status_code != 200:
        return jsonify({'error': 'City not found or API request failed. Please check the provided parameters.'}), 404

    data = response.json()

    if 'city' not in data or 'list' not in data:
        return jsonify({'error': 'Invalid response from weather API. Please try again later.'}), 500

    forecast_data = []
    for item in data['list']:
        forecast_data.append({
            'datetime': item.get('dt_txt', 'N/A'),
            'temperature': item['main'].get('temp', 'N/A'),
            'description': item['weather'][0].get('description', 'No description available') if item['weather'] else 'No description available',
            'humidity': item['main'].get('humidity', 'N/A'),
            'wind_speed': item['wind'].get('speed', 'N/A')
        })

    return jsonify({
        'city': data['city'].get('name', 'N/A'),
        'forecast': forecast_data,
        'units': 'metric' if units == 'metric' else 'imperial'
    })


if __name__ == '__main__':
    app.run(debug=True)
