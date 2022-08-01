import requests
from dotenv import load_dotenv
import os
from typing import Dict

load_dotenv()

API_KEY = os.getenv('API_KEY')

# country = "tr"
# city = "antalya"

target_dict = {"tr": ["antalya", "istambul", "ankara", "izmir"],
               "esp": ["barcelona", "madrid", "vigo", "santander", "malaga"]}


def get_weather_info(country: str, city: str) -> Dict:
    try:
        r = requests.get(f"https://api.weatherbit.io/v2.0/current?city={city}&country={country}&key={API_KEY}")
        return r.json()["data"][0]
    except requests.exceptions.RequestException:
        pass

# Build dict of required info

# Reported in file


if __name__ == '__main__':
    for country, cities in target_dict.items():
        for city in cities:
            get_weather_info(country, city)

    # print(get_weather_info(target_dict))
