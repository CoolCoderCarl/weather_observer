import logging
import os
from datetime import datetime
from typing import List

import requests
from pygismeteo import Gismeteo
from pytz import timezone

# Using in get_current_city func to retrieve current city name
IP_SITE = "http://ipinfo.io/"
OPEN_ELEVATION_API = "https://api.open-elevation.com/api/v1/lookup?locations="

# Input file
CITIES_FILE = "cities.txt"

# Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.ERROR
)


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


if __name__ == "__main__":
    pass
