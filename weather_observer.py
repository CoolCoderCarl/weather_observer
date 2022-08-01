import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')

country = "tr"

city = "antalya"

target_dict = {"tr" :["antalya", "istambul", "ankara", "izmir"],
                "esp": ["barcelona", "madrid", "vigo", "santander", "malaga"]}


# Send request return json string
def get_weather_info(target_dict: dict):
    # r = requests.get(f"https://api.weatherbit.io/v2.0/current?city={city}&country={country}&key={API_KEY}")
    # return r.json()["data"][0]
    for k, v in target_dict.items():
        for i in v:
            print(k, i)

# Build dict of required info

# Reported in file

if __name__ == '__main__':
    print(get_weather_info(target_dict))