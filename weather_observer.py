import codecs
import os
from datetime import datetime
from typing import Dict, List

import requests
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from pytz import timezone
from timezonefinder import TimezoneFinder

load_dotenv()

# As args
API_KEY = os.getenv("API_KEY")
CITIES_FILE = "cities.txt"

REPORT_NAME = "weather_report_"
REPORT_FORMAT = ".md"

REPORT_TIME = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")

# Add time to report
# Args like - file - input-file (if) - output-file (of) ???
# Report in console, if passed special args - file - report to file
# By default report about local timezone the program currently executed


required_names = [
    "relative humidity",
    "part of day",
    "pressure",
    "cloud percents",
    "solar radiation",
    "wind speed",
    "wind direction",
    "sea level pressure",
    "snowfall",
    "temperature",
    "apparent temperature",
]

ignored_values = [
    "lon",
    "timezone",
    "ob_time",
    "country_code",
    "ts",
    "state_code",
    "city_name",
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


def request_weather_info(country_code: str, city_name: str) -> Dict:
    """
    Send GET request to weatherbit resource fetching info about weather about transferred countries & cities
    API_KEY must to be placed in .env file, if not - unhandled exception will throw. For more info look in README.md
    :param country_code:
    :param city_name:
    :return:
    """
    try:
        r = requests.get(
            f"https://api.weatherbit.io/v2.0/current?city={city_name}&country={country_code}&key={API_KEY}"
        )
        return r.json()["data"][0]
    except requests.exceptions.RequestException:
        pass


def prepare_weather_info(
    country_name: str, country_code: str, city_name: str, timezone_by_city: str
):
    """
    Prepare weather information to better writing into report file
    After result is ready, pass it to the report_weather_info func
    :param country_name:
    :param country_code:
    :param city_name:
    :param timezone_by_city:
    :return:
    """
    required_values = []
    for k, v in request_weather_info(country_code, city_name).items():
        if k in ignored_values:
            pass
        else:
            required_values.append(v)
    result = {
        required_names[idx]: required_values[idx] for idx in range(len(required_names))
    }

    report_weather_info(REPORT_TIME, result, city_name, timezone_by_city, country_name)


def report_weather_info(
    report_time: str,
    weather_data: dict,
    city_name: str,
    timezone_by_city: str,
    country_name: str,
):
    """
    Report weather information to file with timestamp
    :param report_time:
    :param weather_data:
    :param city_name:
    :param timezone_by_city:
    :param country_name:
    :return:
    """
    with codecs.open(
        f"{REPORT_NAME}{report_time}{REPORT_FORMAT}", "a", "utf-8"
    ) as report:
        report.write(
            f"## Country: {country_name} | City name: {city_name.capitalize()} \n"
        )
        report.write(f"### Timezone: {timezone_by_city}  \n")
        for key, values in weather_data.items():
            if key in ["relative humidity", "cloud percents"]:
                report.write(f"{key.capitalize()}: {values}%  ")
            elif key in ["pressure", "sea level pressure"]:
                report.write(f"{key.capitalize()}: {values} mb  ")
            elif key in "solar radiation":
                report.write(f"{key.capitalize()}: {values} Watt/m^2  ")
            elif key in "solar radiation":
                report.write(f"{key.capitalize()}: {values} m/s  ")
            elif key in "snowfall":
                report.write(f"{key.capitalize()}: {values} mm/hr  ")
            elif key in ["temperature", "apparent temperature"]:
                report.write(f"{key.capitalize()}: {values} C  ")
            else:
                report.write(f"{key.capitalize()}: {values}  ")
            report.write("\n")
        report.write("\n")


def load_cities_from_file() -> List[str]:
    try:
        with open(CITIES_FILE, "r") as cities_file:
            cities = cities_file.read().split()
        return cities
    except FileNotFoundError as file_not_found_err:
        print(file_not_found_err)


def prepare_target_location_info():
    """
    Prepare info such as country name, country code, city name and timezone for target city,
    then pass it to next func prepare_weather_info
    :return:
    """
    geolocator = Nominatim(user_agent="geoapiExercises")
    for city_name in load_cities_from_file():
        location = geolocator.geocode(city_name)

        obj = TimezoneFinder()
        timezone_by_city = obj.timezone_at(
            lng=location.longitude, lat=location.latitude
        )

        loc_ad = geolocator.reverse(
            str(location.latitude) + "," + str(location.longitude)
        )
        full_address_by_ll = loc_ad.raw["address"]

        country_code = full_address_by_ll.get(
            "country_code", ""
        )  # Verification with city from file & city from this output
        country_name = full_address_by_ll.get("country", "")

        prepare_weather_info(country_name, country_code, city_name, timezone_by_city)


if __name__ == "__main__":
    prepare_target_location_info()
