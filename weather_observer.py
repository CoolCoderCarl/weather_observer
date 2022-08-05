import argparse
import codecs
import os
import sys
import time
from datetime import datetime
from typing import Dict, List

import requests
from geopy.geocoders import Nominatim
from pytz import timezone
from timezonefinder import TimezoneFinder

# Input file
CITIES_FILE = "cities.txt"

# Output file
REPORT_NAME = "weather_report_"
REPORT_FORMAT = ".md"

# Time when program execution started
start_time = time.time()

# Using in get_current_city func to retrieve current city name
IP_SITE = "http://ipinfo.io/"
OPEN_ELEVATION_API = "https://api.open-elevation.com/api/v1/lookup?locations="

REPORT_TIME = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")

# Conversion for pressure
KPA = 0.1  # Kilo Pascal
MMHG = 0.750062  # Millimeter of mercury


required_values = [
    "relative humidity",
    "part of day",
    "pressure",
    "cloud percents",
    "solar radiation",
    "wind speed",
    "wind direction",
    "sea level pressure",
    "snowfall",
    "uv",
    "aqi",
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
    "precip",
    "wind_dir",
    "sunrise",
    "ghi",
    "dhi",
    "lat",
    "weather",
    "datetime",
    "station",
    "elev_angle",
]


def get_args():
    """
    Get arguments from CLI
    :return:
    """
    root_parser = argparse.ArgumentParser(
        prog="observer",
        description="""Report about weather""",
        epilog="""(c) CoolCoderCarl""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    root_parser.add_argument(
        "--api-key",
        dest="apikey",
        help="API key using for fetch info about weather",
        type=str,
    )

    root_parser.add_argument(
        "--file", dest="file", action=argparse.BooleanOptionalAction
    )

    root_parser.add_argument(
        "--local", dest="local", action=argparse.BooleanOptionalAction
    )

    root_parser.add_argument(
        "-v", "--verbosity", dest="verbosity", action=argparse.BooleanOptionalAction
    )

    return root_parser


# Shortening
namespace = get_args().parse_args(sys.argv[1:])


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
    :param country_code:
    :param city_name:
    :return:
    """
    try:
        r = requests.get(
            f"https://api.weatherbit.io/v2.0/current?city={city_name}&country={country_code}&key={namespace.apikey}"
        )
        return r.json()["data"][0]
    except requests.exceptions.RequestException as req_ex:
        print(req_ex)


def calculate_uv_level(uv_value: float) -> str:
    """
    Passed UV value as float and return string value on the scale
    :param uv_value:
    :return:
    """
    if 0.0 <= uv_value <= 2.9:
        return "green"
    elif 3.0 <= uv_value <= 5.9:
        return "yellow"
    elif 6.0 <= uv_value <= 7.9:
        return "orange"
    elif 8.0 <= uv_value <= 10.9:
        return "red"
    elif 11.0 <= uv_value:
        return "purple"


def calculate_aqi_level(aqi_value: int) -> str:
    """
    Passed Air Quality Index value as integer and return string value on the scale
    :param aqi_value:
    :return:
    """
    if 0 <= aqi_value <= 33:
        return "very good"
    elif 34 <= aqi_value <= 66:
        return "good"
    elif 67 <= aqi_value <= 99:
        return "fair"
    elif 100 <= aqi_value <= 149:
        return "poor"
    elif 150 <= aqi_value <= 200:
        return "very poor"
    elif 200 <= aqi_value:
        return "hazardous"


def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert celsius to fahrenheit
    :param celsius:
    :return:
    """
    return (celsius * 9 / 5) + 32


def celsius_to_kelvin(celsius: float) -> float:
    """
    Convert celsius to kelvin
    :param celsius:
    :return:
    """
    return celsius + 273.15


def prepare_weather_info(
    country_name: str,
    country_code: str,
    city_name: str,
    timezone_by_city: str,
    elevation: int,
):
    """
    Prepare weather information to better writing into report file
    After result is ready, pass it to the report_weather_info func
    :param country_name:
    :param country_code:
    :param city_name:
    :param timezone_by_city:
    :param elevation:
    :return:
    """
    report_values = []
    for k, v in request_weather_info(country_code, city_name).items():
        if k in ignored_values:
            pass
        else:
            report_values.append(v)
    result = {
        required_values[idx]: report_values[idx] for idx in range(len(required_values))
    }

    report_weather_info(
        REPORT_TIME, result, city_name, timezone_by_city, country_name, elevation
    )


def report_to_console(
    weather_data: dict,
    city_name: str,
    timezone_by_city: str,
    country_name: str,
    elevation: int,
):
    """
    Report info about weather to console
    :param weather_data:
    :param city_name:
    :param timezone_by_city:
    :param country_name:
    :param elevation:
    :return:
    """
    print()
    print(f"## Country: {country_name} | City name: {city_name.capitalize()}")
    print(f"### Timezone: {timezone_by_city}")
    print(
        f"#### Time in location: {get_time_by_timezone(timezone_name=timezone_by_city)}"
    )
    print(f"Elevation under sea level: {elevation} m")
    for key, values in weather_data.items():
        if key in ["relative humidity", "cloud percents"]:
            print(f"{key.capitalize()}: {values}%")
        elif key in ["pressure", "sea level pressure"]:
            print(
                f"{key.capitalize()}: {round(values, 2)} mb | {round(values*MMHG,2)} mmHg | {round(values*KPA, 2)} kPa"
            )
        elif key in "solar radiation":
            print(f"{key.capitalize()}: {values} Watt/m^2")
        elif key in "wind speed":
            print(f"{key.capitalize()}: {values} m/s")
        elif key in "snowfall":
            print(f"{key.capitalize()}: {values} mm/hr")
        elif key in "uv":
            print(
                f"{key.upper()}: {values} - {calculate_uv_level(round(values, 1)).capitalize()}"
            )
        elif key in "aqi":
            print(
                f"{key.upper()}: {values} - {calculate_aqi_level(values).capitalize()}"
            )
        elif key in ["temperature", "apparent temperature"]:
            print(
                f"{key.capitalize()}: {values} C | {round(celsius_to_fahrenheit(values), 1)} F | {round(celsius_to_kelvin(values),1)} K"
            )
        else:
            print(f"{key.capitalize()}: {values}")
    input("Enter any key to escape...")


def report_to_file(
    report_time: str,
    weather_data: dict,
    city_name: str,
    timezone_by_city: str,
    country_name: str,
    elevation: int,
):
    """
    Report info about weather to file with timestamp
    :param report_time:
    :param weather_data:
    :param city_name:
    :param timezone_by_city:
    :param country_name:
    :param elevation:
    :return:
    """
    with codecs.open(
        f"{REPORT_NAME}{report_time}{REPORT_FORMAT}", "a", "utf-8"
    ) as report:
        if namespace.verbosity:
            print(f"Gathering info about {city_name.capitalize()} in {country_name}...")
        report.write(
            f"## Country: {country_name} | City name: {city_name.capitalize()}  \n"
        )
        report.write(f"### Timezone: {timezone_by_city}  \n")
        report.write(
            f"#### Time in location {get_time_by_timezone(timezone_name=timezone_by_city)}  \n"
        )
        report.write(f"Elevation under sea level: {elevation} m  \n")
        for key, values in weather_data.items():
            if key in ["relative humidity", "cloud percents"]:
                report.write(f"{key.capitalize()}: {values}%  ")
            elif key in ["pressure", "sea level pressure"]:
                report.write(
                    f"{key.capitalize()}: {round(values, 2)} mb | {round(values*MMHG,2)} mmHg | {round(values*KPA, 2)} kPa"
                )
            elif key in "solar radiation":
                report.write(f"{key.capitalize()}: {values} Watt/m^2  ")
            elif key in "wind speed":
                report.write(f"{key.capitalize()}: {values} m/s  ")
            elif key in "snowfall":
                report.write(f"{key.capitalize()}: {values} mm/hr  ")
            elif key in "uv":
                report.write(
                    f"{key.upper()}: {values} - {calculate_uv_level(round(values, 1)).capitalize()}"
                )
            elif key in "aqi":
                report.write(
                    f"{key.upper()}: {values} - {calculate_aqi_level(values).capitalize()}"
                )
            elif key in ["temperature", "apparent temperature"]:
                report.write(
                    f"{key.capitalize()}: {values} C | {round(celsius_to_fahrenheit(values), 1)} F | {round(celsius_to_kelvin(values),1)} K"
                )
            else:
                report.write(f"{key.capitalize()}: {values}  ")
            report.write("\n")
        if namespace.verbosity:
            print("--- %s seconds ---" % (time.time() - start_time))
        report.write("\n")


def report_weather_info(
    report_time: str,
    weather_data: dict,
    city_name: str,
    timezone_by_city: str,
    country_name: str,
    elevation: int,
):
    """
    Report weather information to console as default or in file with timestamp
    If pass --file as arg switch reporting to file
    Else report to console
    :param report_time:
    :param weather_data:
    :param city_name:
    :param timezone_by_city:
    :param country_name:
    :param elevation:
    :return:
    """
    if namespace.file:
        report_to_file(
            report_time,
            weather_data,
            city_name,
            timezone_by_city,
            country_name,
            elevation,
        )
    else:
        report_to_console(
            weather_data, city_name, timezone_by_city, country_name, elevation
        )


def load_cities_from_file() -> List[str]:
    """
    Load cities from file
    Try to load from file, if exception caught, send message about err
    Finally create new file with current city and return it
    :return:
    """
    try:
        with open(CITIES_FILE, "r") as cities_file:
            cities = cities_file.read().split()
            return cities
    except FileNotFoundError as file_not_found_err:
        print(file_not_found_err)
        print(f"Will create {CITIES_FILE}...")
    finally:
        if os.path.exists(CITIES_FILE):
            pass
        else:
            with open(CITIES_FILE, "w") as cities_file:
                cities_file.write(get_current_city())
            with open(CITIES_FILE, "r") as cities_file:
                cities = cities_file.read().split()
                return cities


def get_current_city() -> str:
    """
    Return city name by trusted provider info
    :return:
    """
    try:
        return requests.get(IP_SITE).json()["city"]
    except requests.exceptions.RequestException as request_exception:
        print(request_exception)


def get_elevation_by_ll(latitude: str, longitude: str) -> int:
    """
    Get elevation(altitude) from open API by latitude & longitude
    :param latitude:
    :param longitude:
    :return:
    """
    try:
        return requests.get(OPEN_ELEVATION_API + latitude + "," + longitude).json()[
            "results"
        ][0]["elevation"]
    except requests.exceptions.RequestException as req_ex:
        print(req_ex)


def prepare_target_location_info(city_name: str):
    """
    Prepare info such as country name, country code, city name and timezone for target city,
    then pass it to next func prepare_weather_info
    :return:
    """
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(city_name)
    longitude = str(location.longitude)
    latitude = str(location.latitude)

    obj = TimezoneFinder()
    timezone_by_city = obj.timezone_at(lng=location.longitude, lat=location.latitude)

    loc_ad = geolocator.reverse(latitude + "," + longitude)
    full_address_by_ll = loc_ad.raw["address"]

    country_code = full_address_by_ll.get("country_code", "")
    country_name = full_address_by_ll.get("country", "")

    prepare_weather_info(
        country_name,
        country_code,
        city_name,
        timezone_by_city,
        get_elevation_by_ll(latitude=latitude, longitude=longitude),
    )


def which_target():
    """
    Decide which target location local or got from file will reported
    :return:
    """
    if namespace.local:
        city_name = get_current_city()
        prepare_target_location_info(city_name)
    else:
        for city_name in load_cities_from_file():
            prepare_target_location_info(city_name)


if __name__ == "__main__":
    if namespace.apikey:
        which_target()
