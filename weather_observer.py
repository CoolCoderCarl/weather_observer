import argparse
import codecs
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List

import requests
import requests as rq
from geopy.geocoders import Nominatim
from pygismeteo import Gismeteo
from pytz import timezone
from timezonefinder import TimezoneFinder

# Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.ERROR
)

# Input file
CITIES_FILE = "cities.txt"

# Output file
REPORT_NAME = "weather_report_"
REPORT_FORMAT = ".md"

# Time when program execution started
START_TIME = time.time()

WEATHER_API = "https://api.weatherbit.io/v2.0/"
# Using in get_current_city func to retrieve current city name
IP_SITE = "http://ipinfo.io/"
OPEN_ELEVATION_API = "https://api.open-elevation.com/api/v1/lookup?locations="

REPORT_TIME = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")

# Conversion for pressure
KPA = 0.1  # Kilo Pascal
MMHG = 0.750062  # Millimeter of mercury


# required_values = [
#     "wind direction",
#     "relative humidity",
#     "part of day",
#     "pressure",
#     "cloud percents",
#     "solar radiation",
#     "wind speed",
#     "sea level pressure",
#     "apparent temperature",
#     "snowfall",
#     "aqi",
#     "uv",
#     "temperature",
# ]
#
# required_values = ["wind_cdir_full", "rh", "pod", "pres", "clouds", "solar_rad",
#                    "wind_spd", "slp", "app_temp", "snow", "aqi", "uv", "temp"]


VALUES_TO_DELETE = [
    "lon",
    "timezone",
    "ob_time",
    "country_code",
    "gust",
    "ts",
    "state_code",
    "city_name",
    "wind_cdir_full",
    "vis",
    "sources",
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

    # Specify filenames ?
    root_parser.add_argument(
        "--input-file",
        dest="infile",
        action=argparse.BooleanOptionalAction,
        help="Get cities from files",
    )

    root_parser.add_argument(
        "--output-file",
        dest="outfile",
        action=argparse.BooleanOptionalAction,
        help="Send report to file",
    )

    root_parser.add_argument(
        "--telegram",
        dest="telegram",
        action=argparse.BooleanOptionalAction,
        help="Send report to telegram",
    )

    root_parser.add_argument(
        "-v",
        "--verbosity",
        dest="verbosity",
        action=argparse.BooleanOptionalAction,
        help="Send messages about processing",
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
            f"{WEATHER_API}current?city={city_name}&country={country_code}&key={namespace.apikey}"
        )
        return r.json()["data"][0]
    except requests.exceptions.RequestException as req_ex:
        logging.error(req_ex)
    except BaseException as base_err:
        logging.error(base_err)


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


def calculate_kp_level(kp_value: int) -> str:
    """
    Passed Kp value as int and return string value on the scale
    The Kp-index describes the disturbance of the Earth’s magnetic field caused by the solar wind
    :param kp_value:
    :return:
    """
    if 0 <= kp_value < 3:
        return "quiet"
    elif kp_value == 3:
        return "unsettled"
    elif kp_value == 4:
        return "active"
    elif kp_value == 5:
        return "minor storm"
    elif kp_value == 6:
        return "moderate storm"
    elif kp_value == 7:
        return "strong storm"
    elif kp_value == 8:
        return "severe storm"
    elif kp_value >= 9:
        return "intense storm"


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
    water_temp: float,
    geomagnetic_field: int,
):
    """
    Prepare weather information to better writing into report file
    After result is ready, pass it to the report_weather_info func
    :param country_name:
    :param country_code:
    :param city_name:
    :param timezone_by_city:
    :param elevation:
    :param water_temp:
    :param geomagnetic_field:
    :return:
    """

    result = request_weather_info(country_code, city_name)
    for v in VALUES_TO_DELETE:
        del result[v]

    report_weather_info(
        REPORT_TIME,
        result,
        city_name,
        timezone_by_city,
        country_name,
        elevation,
        water_temp,
        geomagnetic_field,
    )


def report_to_console(
    weather_data: dict,
    city_name: str,
    timezone_by_city: str,
    country_name: str,
    elevation: int,
    water_temp: float,
    geomagnetic_field: int,
):
    """
    Report info about weather to console
    :param weather_data:
    :param city_name:
    :param timezone_by_city:
    :param country_name:
    :param elevation:
    :param water_temp:
    :param geomagnetic_field:
    :return:
    """
    print()
    print(f"Country: {country_name} | City name: {city_name.capitalize()}")
    print(f"Timezone: {timezone_by_city}")
    print(f"Time in location: {get_time_by_timezone(timezone_name=timezone_by_city)}")
    print(f"Elevation above sea level: {elevation} m")
    print(
        f"Water temperature in location: {water_temp} C "
        f"| {round(celsius_to_fahrenheit(water_temp), 1)} F "
        f"| {round(celsius_to_kelvin(water_temp), 1)} K"
    )
    print(
        f"Geomagnetic field: {geomagnetic_field} - {calculate_kp_level(geomagnetic_field).capitalize()}"
    )
    for key, values in weather_data.items():
        if key in ["rh"]:
            print(f"Relative humidity: {values}%")
        elif key in ["clouds"]:
            print(f"Cloud percents: {values}%")
        elif key in ["pres"]:
            print(
                f"Pressure: {round(values, 2)} mb "
                f"| {round(values*MMHG,2)} mmHg "
                f"| {round(values*KPA, 2)} kPa"
            )
        elif key in ["slp"]:
            print(
                f"Sea level ressure: {round(values, 2)} mb "
                f"| {round(values*MMHG,2)} mmHg "
                f"| {round(values*KPA, 2)} kPa"
            )
        elif key in ["solar_rad"]:
            print(f"Solar radiation: {values} Watt/m^2")
        elif key in ["wind_spd"]:
            print(f"Wind speed: {values} m/s")
        elif key in ["wind_cdir"]:
            print(f"Wind direction: {values}")
        elif key in ["snow"]:
            print(f"Snowfall: {values} mm/hr")
        elif key in ["uv"]:
            print(
                f"{key.upper()}: {values} - {calculate_uv_level(round(values, 1)).capitalize()}"
            )
        elif key in ["aqi"]:
            print(
                f"{key.upper()}: {values} - {calculate_aqi_level(values).capitalize()}"
            )
        elif key in ["temp"]:
            print(
                f"Temperature: {values} C "
                f"| {round(celsius_to_fahrenheit(values), 1)} F "
                f"| {round(celsius_to_kelvin(values),1)} K"
            )
        elif key in ["app_temp"]:
            print(
                f"Apparent temperature: {values} C "
                f"| {round(celsius_to_fahrenheit(values), 1)} F "
                f"| {round(celsius_to_kelvin(values),1)} K"
            )
        elif key in ["pod"]:
            print(f"Part of a day: {values}")
        else:
            print(f"{key.capitalize()}: {values}")
    input("Enter any key to escape...")


def report_to_telegram(
    weather_data: dict,
    city_name: str,
    timezone_by_city: str,
    country_name: str,
    elevation: int,
    water_temp: float,
    geomagnetic_field: int,
):
    """
    Report info about weather to telegram
    :param weather_data:
    :param city_name:
    :param timezone_by_city:
    :param country_name:
    :param elevation:
    :param water_temp:
    :param geomagnetic_field:
    :return:
    """
    try:
        TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
        TELEGRAM_API_URL = (
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        )
        TELEGRAM_CHAT_ID = os.environ["TELE_CHAT_ID"]

        try:
            response = rq.post(
                TELEGRAM_API_URL,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": f"## Country: {country_name} | City name: {city_name.capitalize()}  \n"
                    f"\n"
                    f"### Timezone: {timezone_by_city}  \n"
                    f"\n"
                    f"#### Time in location {get_time_by_timezone(timezone_name=timezone_by_city)}  \n"
                    f"\n"
                    f"Elevation under sea level: {elevation} m  \n"
                    f"\n"
                    f"Water temperature in location: {water_temp} C "
                    f"| {round(celsius_to_fahrenheit(water_temp), 1)} F "
                    f"| {round(celsius_to_kelvin(water_temp),1)} K  \n"
                    f"\n"
                    f"Geomagnetic field: {geomagnetic_field} - "
                    f"{calculate_kp_level(geomagnetic_field).capitalize()}  \n"
                    f"\n"
                    f"Relative humidity: {weather_data['rh']}\n"
                    f"\n"
                    f"Cloud percents: {weather_data['clouds']}%\n"
                    f"\n"
                    f"Pressure: {weather_data['pres']}\n"
                    f"\n"
                    f"Relative humidity: {round(weather_data['slp'],2)} mb "
                    f"| {round(weather_data['slp'] * MMHG, 2)} mmHg "
                    f"| {round(weather_data['slp'] * KPA, 2)} kPa\n"
                    f"\n"
                    f"**Solar radiation: {weather_data['solar_rad']} Watt/m^2\n"
                    f"\n"
                    f"Wind speed: {weather_data['wind_spd']} m/s\n"
                    f"\n"
                    f"Wind direction: {weather_data['wind_cdir']}\n"
                    f"\n"
                    f"Snowfall: {weather_data['snow']} mm/hr\n"
                    f"\n"
                    f"UV (UltraViolet): {weather_data['uv']} - "
                    f"{calculate_uv_level(round(weather_data['uv'], 1)).capitalize()}\n"
                    f"\n"
                    f"AQI (Air Quality Index): {weather_data['aqi']} - "
                    f"{calculate_aqi_level(weather_data['aqi']).capitalize()}\n"
                    f"\n"
                    f"Temperature: {weather_data['temp']} C "
                    f"| {round(celsius_to_fahrenheit(weather_data['temp']), 1)} F "
                    f"| {round(celsius_to_kelvin(weather_data['temp']), 1)} K\n"
                    f"\n"
                    f"Apparent temperature: {weather_data['app_temp']} C "
                    f"| {round(celsius_to_fahrenheit(weather_data['app_temp']), 1)} F "
                    f"| {round(celsius_to_kelvin(weather_data['app_temp']), 1)} K \n"
                    f"\n"
                    f"Part of a day: {weather_data['pod']}\n",
                },
            )
            if response.status_code == 200:
                logging.info(
                    f"Sent: {response.reason}. Status code: {response.status_code}"
                )
            else:
                logging.error(
                    f"Not sent: {response.reason}. Status code: {response.status_code}"
                )
        except KeyError as keyerr:
            logging.error(keyerr)
    except KeyError as key_err:
        logging.error(key_err)
    except Exception as err:
        logging.error(err)


def report_to_file(
    report_time: str,
    weather_data: dict,
    city_name: str,
    timezone_by_city: str,
    country_name: str,
    elevation: int,
    water_temp: float,
    geomagnetic_field: int,
):
    """
    Report info about weather to file with timestamp
    :param report_time:
    :param weather_data:
    :param city_name:
    :param timezone_by_city:
    :param country_name:
    :param elevation:
    :param water_temp:
    :param geomagnetic_field:
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
        report.write(f"**Elevation under sea level:** {elevation} m  \n")
        report.write(
            f"**Water temperature in location:** {water_temp} C "
            f"| {round(celsius_to_fahrenheit(water_temp), 1)} F "
            f"| {round(celsius_to_kelvin(water_temp),1)} K  \n"
        )
        report.write(
            f"Geomagnetic field: {geomagnetic_field} - {calculate_kp_level(geomagnetic_field).capitalize()}  \n"
        )
        for key, values in weather_data.items():
            if key in ["rh"]:
                report.write(f"**Relative humidity:** {values}% \n")
            elif key in ["clouds"]:
                report.write(f"Cloud percents: {values}% \n")
            elif key in ["pres"]:
                report.write(
                    f"**Pressure:** {round(values, 2)} mb "
                    f"| {round(values * MMHG, 2)} mmHg "
                    f"| {round(values * KPA, 2)} kPa \n"
                )
            elif key in ["slp"]:
                report.write(
                    f"Sea level ressure: {round(values, 2)} mb "
                    f"| {round(values * MMHG, 2)} mmHg "
                    f"| {round(values * KPA, 2)} kPa \n"
                )
            elif key in ["solar_rad"]:
                report.write(f"**Solar radiation:** {values} Watt/m^2 \n")
            elif key in ["wind_spd"]:
                report.write(f"Wind speed: {values} m/s \n")
            elif key in ["wind_cdir"]:
                report.write(f"Wind direction: {values} \n")
            elif key in ["snow"]:
                report.write(f"Snowfall: {values} mm/hr \n")
            elif key in ["uv"]:
                report.write(
                    f"{key.upper()}: {values} - {calculate_uv_level(round(values, 1)).capitalize()} \n"
                )
            elif key in ["aqi"]:
                report.write(
                    f"{key.upper()}: {values} - {calculate_aqi_level(values).capitalize()} \n"
                )
            elif key in ["temp"]:
                report.write(
                    f"**Temperature:** {values} C "
                    f"| {round(celsius_to_fahrenheit(values), 1)} F "
                    f"| {round(celsius_to_kelvin(values), 1)} K \n"
                )
            elif key in ["app_temp"]:
                report.write(
                    f"**Apparent temperature:** {values} C "
                    f"| {round(celsius_to_fahrenheit(values), 1)} F "
                    f"| {round(celsius_to_kelvin(values), 1)} K \n"
                )
            elif key in ["pod"]:
                report.write(f"Part of a day: {values} \n")
            else:
                report.write(f"{key.capitalize()}: {values}  \n")
            report.write("\n")
        report.write("\n")
        if namespace.verbosity:
            print("--- %s seconds ---" % (time.time() - START_TIME))
        report.write("\n")


def report_weather_info(
    report_time: str,
    weather_data: dict,
    city_name: str,
    timezone_by_city: str,
    country_name: str,
    elevation: int,
    water_temp: float,
    geomagnetic_field: int,
):
    """
    Report weather information to console as default or in file with timestamp or in telegram
    If pass --file as arg switch reporting to file
    If pass --telegram as arg switch reporting to telegram
    Else report to console
    :param report_time:
    :param weather_data:
    :param city_name:
    :param timezone_by_city:
    :param country_name:
    :param elevation:
    :param water_temp:
    :param geomagnetic_field:
    :return:
    """
    if namespace.outfile:
        report_to_file(
            report_time,
            weather_data,
            city_name,
            timezone_by_city,
            country_name,
            elevation,
            water_temp,
            geomagnetic_field,
        )
    elif namespace.telegram:
        report_to_telegram(
            weather_data,
            city_name,
            timezone_by_city,
            country_name,
            elevation,
            water_temp,
            geomagnetic_field,
        )
    else:
        report_to_console(
            weather_data,
            city_name,
            timezone_by_city,
            country_name,
            elevation,
            water_temp,
            geomagnetic_field,
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
        logging.error(file_not_found_err)
        logging.info(f"Will create {CITIES_FILE}...")
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
        logging.error(request_exception)


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
        logging.error(req_ex)


def get_water_temp_by_ll(latitude: float, longitude: float) -> float:
    """
    Get water temperature from https://www.gismeteo.com/api/ by latitude & longitude
    :param latitude:
    :param longitude:
    :return:
    """
    gm = Gismeteo()
    city_id = gm.search.by_coordinates(latitude=latitude, longitude=longitude, limit=1)[
        0
    ].id
    return gm.current.by_id(city_id).temperature.water.c


def get_geomagnetic_field_by_ll(latitude: float, longitude: float) -> int:
    """
    Get water temperature from https://www.gismeteo.com/api/ by latitude & longitude
    :param latitude:
    :param longitude:
    :return:
    """
    gm = Gismeteo()
    city_id = gm.search.by_coordinates(latitude=latitude, longitude=longitude, limit=1)[
        0
    ].id
    return gm.current.by_id(city_id).gm


def prepare_target_location_info(city_name: str):
    """
    Prepare info such as country name, country code, city name and timezone for target city,
    then pass it to next func prepare_weather_info
    :return:
    """
    # Separate and return longitude & latitude with different funcs - Class ?
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

    if namespace.telegram:
        while True:
            if get_time_by_timezone(timezone_name=timezone_by_city).split()[1] in [
                "06:00:00",
                "09:00:00",
                "12:00:00",
                "15:00:00",
                "18:00:00",
                "21:00:00",
            ]:
                logging.info("It is time to report !")
                prepare_weather_info(
                    country_name,
                    country_code,
                    city_name,
                    timezone_by_city,
                    get_elevation_by_ll(latitude=latitude, longitude=longitude),
                    get_water_temp_by_ll(
                        latitude=location.latitude, longitude=location.longitude
                    ),
                    get_geomagnetic_field_by_ll(
                        latitude=location.latitude, longitude=location.longitude
                    ),
                )
    else:
        prepare_weather_info(
            country_name,
            country_code,
            city_name,
            timezone_by_city,
            get_elevation_by_ll(latitude=latitude, longitude=longitude),
            get_water_temp_by_ll(
                latitude=location.latitude, longitude=location.longitude
            ),
            get_geomagnetic_field_by_ll(
                latitude=location.latitude, longitude=location.longitude
            ),
        )


def which_target():
    """
    Decide which target location got from file or local will reported
    :return:
    """
    if namespace.infile:
        for city_name in load_cities_from_file():
            prepare_target_location_info(city_name)
    else:
        city_name = get_current_city()
        prepare_target_location_info(city_name)


if __name__ == "__main__":
    if namespace.apikey:
        which_target()
    else:
        logging.error("API key did not provide")
        sys.exit(1)
