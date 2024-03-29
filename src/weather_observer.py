import argparse
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict

import requests
import requests as rq
from geopy.adapters import AdapterHTTPError
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

import calculations
import get_info

# Logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.ERROR)


# Output file
REPORT_NAME = "weather_report_"
REPORT_FORMAT = ".md"

# Time when program execution started
start_time = time.time()

WEATHER_API = "https://api.weatherbit.io/v2.0/"


report_time = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")

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


def request_weather_info(
    country_code: str,
    city_name: str,
) -> Dict[str, any]:
    """
    Send GET request to weatherbit resource fetching info about weather about transferred countries & cities
    :param country_code:
    :param city_name:
    :return:
    """
    try:
        r = requests.get(f"{WEATHER_API}current?city={city_name}&country={country_code}&key={namespace.apikey}")
        return r.json()["data"][0]
    except requests.exceptions.RequestException as req_ex:
        logging.error(f"Err while request weather info from API - {req_ex}")
        return None
    except BaseException as base_err:
        logging.error(f"Base err while request weather info from API - {base_err}")
        return None


def prepare_weather_data(
    country_code: str,
    city_name: str,
) -> Dict[str, any]:
    """
    Prepare weather information to better writing into report file
    :param country_code:
    :param city_name:
    :return:
    """

    result = request_weather_info(
        country_code,
        city_name,
    )

    for v in VALUES_TO_DELETE:
        try:
            del result[v]
        except KeyError as key_err:
            logging.error(f"Key Err while deleting values - {key_err}")
            continue
        except BaseException as base_err:
            logging.error(f"Base Err while deleting values - {base_err}")
            continue
        return result


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
    print(f"Time: {get_info.get_time_by_timezone(timezone_name=timezone_by_city)}")
    print()
    print(f"Part of a day: {weather_data['pod']}")
    print(f"Elevation above sea level: {elevation} m")
    print(f"Geomagnetic field: {geomagnetic_field} - {calculations.calculate_kp_level(geomagnetic_field).capitalize()}")
    print()
    print(
        f"Pressure: {round(weather_data['pres'], 2)} mb "
        f"| {round(weather_data['pres'] * MMHG, 2)} mmHg "
        f"| {round(weather_data['pres'] * KPA, 2)} kPa"
    )
    print(
        f"Sea level pressure: {round(weather_data['slp'], 2)} mb "
        f"| {round(weather_data['slp'] * MMHG, 2)} mmHg "
        f"| {round(weather_data['slp'] * KPA, 2)} kPa"
    )
    print()
    print(f"Wind speed: {weather_data['wind_spd']} m/s")
    print(f"Wind direction: {weather_data['wind_cdir']}")
    print(f"Relative humidity: {weather_data['rh']}%")
    print(f"Cloud percents: {weather_data['clouds']}%")
    print(f"Solar radiation: {weather_data['solar_rad']} Watt/m^2")
    print(f"Snowfall: {weather_data['snow']} mm/hr")
    print()
    print(
        f"UV (UltraViolet): {weather_data['uv']} - "
        f"{calculations.calculate_uv_level(round(weather_data['uv'], 1)).capitalize()}"
    )
    print(
        f"AQI (Air Quality Index): {weather_data['aqi']} - "
        f"{calculations.calculate_aqi_level(weather_data['aqi']).capitalize()}"
    )
    print()
    print(
        f"Temperature: {weather_data['temp']} C "
        f"| {round(calculations.celsius_to_fahrenheit(weather_data['temp']), 1)} F "
        f"| {round(calculations.celsius_to_kelvin(weather_data['temp']), 1)} K"
    )
    print(
        f"Apparent temperature: {weather_data['app_temp']} C "
        f"| {round(calculations.celsius_to_fahrenheit(weather_data['app_temp']), 1)} F "
        f"| {round(calculations.celsius_to_kelvin(weather_data['app_temp']), 1)} K "
    )
    print(
        f"Water temperature: {water_temp} C "
        f"| {round(calculations.celsius_to_fahrenheit(water_temp), 1)} F "
        f"| {round(calculations.celsius_to_kelvin(water_temp), 1)} K  "
    )
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
        TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
        logging.info(f"Report about {city_name} in {country_name} !")
        try:
            response = rq.post(
                TELEGRAM_API_URL,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": f"Country: #{country_name} | City name: #{city_name.capitalize()}"
                    f"\n"
                    f"Timezone: {timezone_by_city}"
                    f"\n"
                    f"Time: {get_info.get_time_by_timezone(timezone_name=timezone_by_city)}"
                    f"\n"
                    f"\n"
                    f"Part of a day: {weather_data['pod']}"
                    f"\n"
                    f"Elevation under sea level: {elevation} m"
                    f"\n"
                    f"Geomagnetic field: {geomagnetic_field} - "
                    f"{calculations.calculate_kp_level(geomagnetic_field).capitalize()}"
                    f"\n"
                    f"\n"
                    f"Pressure: {round(weather_data['pres'], 2)} mb "
                    f"| {round(weather_data['pres']*MMHG,2)} mmHg "
                    f"| {round(weather_data['pres']*KPA, 2)} kPa"
                    f"\n"
                    f"Sea level pressure: {round(weather_data['slp'],2)} mb "
                    f"| {round(weather_data['slp'] * MMHG, 2)} mmHg "
                    f"| {round(weather_data['slp'] * KPA, 2)} kPa"
                    f"\n"
                    f"\n"
                    f"Wind speed: {weather_data['wind_spd']} m/s"
                    f"\n"
                    f"Wind direction: {weather_data['wind_cdir']}"
                    f"\n"
                    f"Relative humidity: {weather_data['rh']}%"
                    f"\n"
                    f"Cloud percents: {weather_data['clouds']}%"
                    f"\n"
                    f"Solar radiation: {weather_data['solar_rad']} Watt/m^2"
                    f"\n"
                    f"Snowfall: {weather_data['snow']} mm/hr\n"
                    f"\n"
                    f"\n"
                    f"UV (UltraViolet): {weather_data['uv']} - "
                    f"{calculations.calculate_uv_level(round(weather_data['uv'], 1)).capitalize()}"
                    f"\n"
                    f"AQI (Air Quality Index): {weather_data['aqi']} - "
                    f"{calculations.calculate_aqi_level(weather_data['aqi']).capitalize()}"
                    f"\n"
                    f"\n"
                    f"Temperature: {weather_data['temp']} C "
                    f"| {round(calculations.celsius_to_fahrenheit(weather_data['temp']), 1)} F "
                    f"| {round(calculations.celsius_to_kelvin(weather_data['temp']), 1)} K"
                    f"\n"
                    f"Apparent temperature: {weather_data['app_temp']} C "
                    f"| {round(calculations.celsius_to_fahrenheit(weather_data['app_temp']), 1)} F "
                    f"| {round(calculations.celsius_to_kelvin(weather_data['app_temp']), 1)} K "
                    f"\n"
                    f"Water temperature: {water_temp} C "
                    f"| {round(calculations.celsius_to_fahrenheit(water_temp), 1)} F "
                    f"| {round(calculations.celsius_to_kelvin(water_temp), 1)} K  "
                    f"\n",
                },
            )
            if response.status_code == 200:
                logging.info(f"Sent: {response.reason}. Status code: {response.status_code}")
            else:
                logging.error(f"Not sent: {response.reason}. Status code: {response.status_code}")
        except KeyError as key_err:
            logging.error(f"Err while post to telegram: {key_err}")
    except KeyError as key_err:
        logging.error(f"Err while loading telegram environment variable: {key_err}")
    except BaseException as err:
        logging.error(f"Base err while loading telegram environment variable: {err}")


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
    with open(
        f"{REPORT_NAME}{report_time}{REPORT_FORMAT}",
        "a",
        encoding="utf-8",
    ) as report:
        if namespace.verbosity:
            print(f"Gathering info about {city_name.capitalize()} in {country_name}...")
        report.write(f"## Country: {country_name} | City name: {city_name.capitalize()}  \n")
        report.write(f"### Timezone: {timezone_by_city}  \n")
        report.write(f"**Elevation under sea level:** {elevation} m  \n")
        report.write(
            f"Geomagnetic field: {geomagnetic_field} - {calculations.calculate_kp_level(geomagnetic_field).capitalize()}  \n"
        )
        report.write(f"Country: {country_name} | City name: {city_name.capitalize()}  \n")
        report.write(f"Timezone: {timezone_by_city}  \n")
        report.write(f"Time: {get_info.get_time_by_timezone(timezone_name=timezone_by_city)}  \n")
        report.write("\n")
        report.write(f"Part of a day: {weather_data['pod']}  \n")
        report.write(f"Elevation above sea level: {elevation} m  \n")
        report.write(
            f"Geomagnetic field: {geomagnetic_field} - {calculations.calculate_kp_level(geomagnetic_field).capitalize()}  \n"
        )
        report.write("\n")
        report.write(
            f"Pressure: {round(weather_data['pres'], 2)} mb "
            f"| {round(weather_data['pres'] * MMHG, 2)} mmHg "
            f"| {round(weather_data['pres'] * KPA, 2)} kPa  \n"
        )
        report.write(
            f"Sea level pressure: {round(weather_data['slp'], 2)} mb "
            f"| {round(weather_data['slp'] * MMHG, 2)} mmHg "
            f"| {round(weather_data['slp'] * KPA, 2)} kPa  \n"
        )
        report.write("\n")
        report.write(f"Wind speed: {weather_data['wind_spd']} m/s  \n")
        report.write(f"Wind direction: {weather_data['wind_cdir']}  \n")
        report.write(f"Relative humidity: {weather_data['rh']}%  \n")
        report.write(f"Cloud percents: {weather_data['clouds']}%  \n")
        report.write(f"**Solar radiation**: {weather_data['solar_rad']} Watt/m^2  \n")
        report.write(f"Snowfall: {weather_data['snow']} mm/hr  \n")
        report.write("\n")
        report.write(
            f"UV (UltraViolet): {weather_data['uv']} - "
            f"{calculations.calculate_uv_level(round(weather_data['uv'], 1)).capitalize()}  \n"
        )
        report.write(
            f"AQI (Air Quality Index): {weather_data['aqi']} - "
            f"{calculations.calculate_aqi_level(weather_data['aqi']).capitalize()}  \n"
        )
        report.write("\n")
        report.write(
            f"**Temperature**: {weather_data['temp']} C "
            f"| {round(calculations.celsius_to_fahrenheit(weather_data['temp']), 1)} F "
            f"| {round(calculations.celsius_to_kelvin(weather_data['temp']), 1)} K  \n"
        )
        report.write(
            f"**Apparent temperature**: {weather_data['app_temp']} C "
            f"| {round(calculations.celsius_to_fahrenheit(weather_data['app_temp']), 1)} F "
            f"| {round(calculations.celsius_to_kelvin(weather_data['app_temp']), 1)} K  \n"
        )
        report.write(
            f"**Water temperature**: {water_temp} C "
            f"| {round(calculations.celsius_to_fahrenheit(water_temp), 1)} F "
            f"| {round(calculations.celsius_to_kelvin(water_temp), 1)} K  \n"
        )
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


def prepare_target_location_info(
    city_name: str,
) -> Dict[str, any]:
    """
    Prepare info such as country name, country code, city name and timezone for target city
    :param city_name:
    :return:
    """
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(city_name)
        longitude = str(location.longitude)
        latitude = str(location.latitude)

        obj = TimezoneFinder()
        timezone_by_city = obj.timezone_at(
            lng=location.longitude,
            lat=location.latitude,
        )

        loc_ad = geolocator.reverse(latitude + "," + longitude)
        full_address_by_ll = loc_ad.raw["address"]

        country_code = full_address_by_ll.get(
            "country_code",
            "",
        )
        country_name = full_address_by_ll.get(
            "country",
            "",
        )

        return {
            "location": location,
            "longitude": longitude,
            "latitude": latitude,
            "country_name": country_name,
            "country_code": country_code,
            "timezone_by_city": timezone_by_city,
        }
    except AdapterHTTPError as adapter_http_err:
        logging.error(f"Adapter HTTP Err while preparing info about target location - {adapter_http_err}")
        return None
    except BaseException as base_err:
        logging.error(f"Base Err while preparing info about target location - {base_err}")
        return None


def main():
    if namespace.telegram:
        logging.info("Going to send reports to telegram...")
        cities = get_info.load_cities_from_file()
        while True:
            if namespace.infile:
                for city_name in cities:
                    prepared_t_l_i = prepare_target_location_info(city_name)
                    if get_info.get_time_by_timezone(timezone_name=prepared_t_l_i["timezone_by_city"]).split()[1] in [
                        "06:00:00",
                        "08:00:00",
                        "10:00:00",
                        "12:00:00",
                        "14:00:00",
                        "16:00:00",
                        "18:00:00",
                        "20:00:00",
                        "22:00:00",
                    ]:
                        logging.info(f"It is time to report ! Will report about - {city_name}")
                        report_weather_info(
                            report_time=report_time,
                            weather_data=prepare_weather_data(
                                prepared_t_l_i["country_name"],
                                city_name,
                            ),
                            city_name=city_name,
                            timezone_by_city=prepared_t_l_i["timezone_by_city"],
                            country_name=prepared_t_l_i["country_name"],
                            elevation=get_info.get_elevation_by_ll(
                                latitude=prepared_t_l_i["latitude"],
                                longitude=prepared_t_l_i["longitude"],
                            ),
                            water_temp=get_info.get_water_temp_by_ll(
                                latitude=prepared_t_l_i["latitude"],
                                longitude=prepared_t_l_i["longitude"],
                            ),
                            geomagnetic_field=get_info.get_geomagnetic_field_by_ll(
                                latitude=prepared_t_l_i["location"].latitude,
                                longitude=prepared_t_l_i["location"].longitude,
                            ),
                        )
            else:
                logging.info("Going to load cities by ...")
                city_name = get_info.get_current_city()
                prepared_t_l_i = prepare_target_location_info(city_name)
                if get_info.get_time_by_timezone(timezone_name=prepared_t_l_i["timezone_by_city"]).split()[1] in [
                    "06:00:00",
                    "08:00:00",
                    "10:00:00",
                    "12:00:00",
                    "14:00:00",
                    "16:00:00",
                    "18:00:00",
                    "20:00:00",
                    "22:00:00",
                ]:
                    logging.info(f"It is time to report ! Will report about - {city_name}")
                    report_weather_info(
                        report_time=report_time,
                        weather_data=prepare_weather_data(
                            prepared_t_l_i["country_name"],
                            city_name,
                        ),
                        city_name=city_name,
                        timezone_by_city=prepared_t_l_i["timezone_by_city"],
                        country_name=prepared_t_l_i["country_name"],
                        elevation=get_info.get_elevation_by_ll(
                            latitude=prepared_t_l_i["latitude"],
                            longitude=prepared_t_l_i["longitude"],
                        ),
                        water_temp=get_info.get_water_temp_by_ll(
                            latitude=prepared_t_l_i["latitude"],
                            longitude=prepared_t_l_i["longitude"],
                        ),
                        geomagnetic_field=get_info.get_geomagnetic_field_by_ll(
                            latitude=prepared_t_l_i["location"].latitude,
                            longitude=prepared_t_l_i["location"].longitude,
                        ),
                    )
    else:
        city_name = get_info.get_current_city()
        prepared_t_l_i = prepare_target_location_info(city_name)
        report_weather_info(
            report_time=report_time,
            weather_data=prepare_weather_data(
                prepared_t_l_i["country_name"],
                city_name,
            ),
            city_name=city_name,
            timezone_by_city=prepared_t_l_i["timezone_by_city"],
            country_name=prepared_t_l_i["country_name"],
            elevation=get_info.get_elevation_by_ll(
                latitude=prepared_t_l_i["latitude"],
                longitude=prepared_t_l_i["longitude"],
            ),
            water_temp=get_info.get_water_temp_by_ll(
                latitude=prepared_t_l_i["location"].latitude,
                longitude=prepared_t_l_i["location"].longitude,
            ),
            geomagnetic_field=get_info.get_geomagnetic_field_by_ll(
                latitude=prepared_t_l_i["location"].latitude,
                longitude=prepared_t_l_i["location"].longitude,
            ),
        )


if __name__ == "__main__":
    if namespace.apikey:
        logging.info("Starting up...")
        main()
    else:
        logging.error("API key did not provide")
        sys.exit(1)
