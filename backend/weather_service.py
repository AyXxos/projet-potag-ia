import requests
from datetime import datetime, timedelta

# Cache simple en mémoire
weather_cache = {}

def get_weather_forecast(lat: float, lon: float, days: int = 7):
    """
    Récupère les prévisions météo sur plusieurs jours pour l'IA.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,soil_temperature_0cm",
        "daily": "temperature_2m_min",
        "timezone": "auto",
        "forecast_days": days
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        
        forecast = []
        for i in range(days):
            # Index pour les données horaires (24h par jour)
            start_h = i * 24
            end_h = (i + 1) * 24
            
            temp_air = sum(raw_data["hourly"]["temperature_2m"][start_h:end_h]) / 24
            temp_sol = sum(raw_data["hourly"]["soil_temperature_0cm"][start_h:end_h]) / 24
            hum = sum(raw_data["hourly"]["relative_humidity_2m"][start_h:end_h]) / 24
            
            forecast.append({
                "date": raw_data["daily"]["time"][i],
                "temp_air": round(temp_air, 2),
                "temp_sol": round(temp_sol, 2),
                "humidite_sol": int(hum),
                "prevision_gelee": 1 if raw_data["daily"]["temperature_2m_min"][i] < 2 else 0
            })
        return forecast
    except Exception as e:
        print(f"Erreur Forecast API: {e}")
        return []
