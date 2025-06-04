import requests
from statistics import mean
from collections import Counter

def get_weather(city, api_key):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=1&aqi=no&alerts=no"
    response = requests.get(url)
    data = response.json()

    try:
        hours = data['forecast']['forecastday'][0]['hour']
        relevant_hours = [h for h in hours if 8 <= int(h['time'].split(' ')[1].split(':')[0]) <= 20]

        temps = [h['temp_c'] for h in relevant_hours]
        conditions = [h['condition']['text'] for h in relevant_hours]
        icons = [h['condition']['icon'] for h in relevant_hours]

        avg_temp = round(mean(temps), 1)
        common_condition = Counter(conditions).most_common(1)[0][0]
        common_icon = Counter(icons).most_common(1)[0][0]

        return avg_temp, common_condition, f"https:{common_icon}"
    except Exception as e:
        print(f"Erreur lors du traitement météo : {e}")
        return None, None, None


import requests