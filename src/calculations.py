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
