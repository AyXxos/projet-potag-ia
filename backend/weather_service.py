import requests
from datetime import datetime, timedelta

# Cache simple en mémoire
weather_cache = {}

def get_weather_forecast(lat: float, lon: float, days: int = 7):
    """
    Récupère les prévisions météo sur plusieurs jours pour l'IA.
    Utilise Open-Meteo (max 16 jours) puis un fallback cyclique pour atteindre 'days'.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    # Open-Meteo gratuit permet max 16 jours
    api_days = min(days, 16)
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,soil_temperature_0cm",
        "daily": "temperature_2m_min",
        "timezone": "auto",
        "forecast_days": api_days
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        
        forecast = []
        # On utilise le nombre de jours réellement retourné par l'API dans "daily"
        available_api_days = len(raw_data.get("daily", {}).get("time", []))
        
        for i in range(available_api_days):
            # Index pour les données horaires (24h par jour)
            start_h = i * 24
            end_h = (i + 1) * 24
            
            # Sécurité sur le slicing et les valeurs None
            h_temps = [t for t in raw_data["hourly"]["temperature_2m"][start_h:end_h] if t is not None]
            h_soil = [t for t in raw_data["hourly"]["soil_temperature_0cm"][start_h:end_h] if t is not None]
            h_hum = [h for h in raw_data["hourly"]["relative_humidity_2m"][start_h:end_h] if h is not None]
            
            if not h_temps: 
                # Si pas de données d'air, on saute le jour ou on met des valeurs par défaut
                if i > 0: # On prend la veille si possible
                    ref = forecast[-1]
                    forecast.append({
                        "date": raw_data["daily"]["time"][i],
                        "temp_air": ref["temp_air"],
                        "temp_sol": ref["temp_sol"],
                        "humidite_sol": ref["humidite_sol"],
                        "prevision_gelee": 1 if raw_data["daily"]["temperature_2m_min"][i] < 2 else 0
                    })
                continue
            
            temp_air = sum(h_temps) / len(h_temps)
            temp_sol = sum(h_soil) / len(h_soil) if h_soil else temp_air - 2
            hum = sum(h_hum) / len(h_hum) if h_hum else 60
            
            forecast.append({
                "date": raw_data["daily"]["time"][i],
                "temp_air": round(temp_air, 2),
                "temp_sol": round(temp_sol, 2),
                "humidite_sol": int(hum),
                "prevision_gelee": 1 if raw_data["daily"]["temperature_2m_min"][i] < 2 else 0
            })

        if not forecast:
            print("⚠️ API Météo indisponible, utilisation de données fictives (MOCK)")
            for i in range(days):
                date_str = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                forecast.append({
                    "date": date_str,
                    "temp_air": 22.5,
                    "temp_sol": 18.0,
                    "humidite_sol": 65,
                    "prevision_gelee": 0
                })
            return forecast

        # Fallback pour atteindre le nombre de jours demandés (ex: 60)
        if days > len(forecast):
            initial_len = len(forecast)
            last_date_str = forecast[-1]["date"]
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
            
            num_to_add = days - initial_len
            for i in range(1, num_to_add + 1):
                # On boucle sur les données existantes pour simuler le futur
                ref = forecast[(i - 1) % initial_len]
                next_date = (last_date + timedelta(days=i)).strftime("%Y-%m-%d")
                
                forecast.append({
                    "date": next_date,
                    "temp_air": ref["temp_air"],
                    "temp_sol": ref["temp_sol"],
                    "humidite_sol": ref["humidite_sol"],
                    "prevision_gelee": ref["prevision_gelee"],
                })
                
        return forecast[:days]
    except Exception as e:
        print(f"Erreur Forecast API: {e}, utilisation de données fictives (MOCK)")
        mock_forecast = []
        for i in range(days):
            date_str = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            mock_forecast.append({
                "date": date_str,
                "temp_air": 22.5,
                "temp_sol": 18.0,
                "humidite_sol": 65,
                "prevision_gelee": 0
            })
        return mock_forecast
