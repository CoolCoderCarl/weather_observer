import codecs
import os
from datetime import datetime
from typing import Dict

import requests
from dotenv import load_dotenv
from pytz import timezone

load_dotenv()

API_KEY = os.getenv("API_KEY")


timestamp = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")

# Get from file
target_dict = {
    "tr": ["antalya", "istambul", "ankara", "izmir"],
    "esp": ["barcelona", "madrid", "vigo", "santander", "malaga"],
}


required_names = [
    "relative humidity",
    "part of day",
    "pressure",
    "timezone",
    "cloud percents",
    "solar radiation",
    "city",
    "wind speed",
    "wind direction",
    "sea level pressure",
    "snowfall",
    "temperature",
    "apparent temperature",
]

ignored_values = [
    "lon",
    "ob_time",
    "country_code",
    "ts",
    "state_code",
    "wind_cdir_full",
    "vis",
    "h_angle",
    "sunset",
    "dni",
    "dewpt",
    "uv",
    "precip",
    "wind_dir",
    "sunrise",
    "ghi",
    "dhi",
    "aqi",
    "lat",
    "weather",
    "datetime",
    "station",
    "elev_angle",
]


# TO DO
def get_time_by_timezone(timezone_name: str) -> str:
    """
    Get current time in UTC the convert to passed time zone
    :param timezone_name: The name like Europe/Madrid
    :return:
    """
    date_time_format = "%Y-%m-%d %H:%M:%S %z"

    now_utc = datetime.now(timezone("UTC"))

    now_timezone = now_utc.astimezone(timezone(timezone_name))
    return now_timezone.strftime(date_time_format)


def request_weather_info(country: str, city: str) -> Dict:
    try:
        r = requests.get(
            f"https://api.weatherbit.io/v2.0/current?city={city}&country={country}&key={API_KEY}"
        )
        return r.json()["data"][0]
    except requests.exceptions.RequestException:
        pass


def prepare_weather_info():
    for country, cities in target_dict.items():
        for city in cities:
            required_values = []
            for k, v in request_weather_info(country, city).items():
                if k in ignored_values:
                    pass
                else:
                    required_values.append(v)
            result = {
                required_names[idx]: required_values[idx]
                for idx in range(len(required_names))
            }
            report_weather_info(timestamp, result)


def report_weather_info(report_time: str, weather_data: dict):
    with codecs.open("report_" + report_time + ".md", "a", "utf-8") as report:
        for key, values in weather_data.items():
            report.write(f"{key.capitalize()}: {values}  ")
            report.write("\n")
        report.write("\n")


if __name__ == "__main__":
    prepare_weather_info()
