FROM python:3.9-alpine as builder

WORKDIR /opt

COPY ["weather_observer.py", "/opt/"]
COPY requirements.txt requirements.txt

RUN python -m pip3 install --upgrade pip3

RUN pip3 install --no-cache-dir -r requirements.txt

FROM builder

ENTRYPOINT ["python3", "/opt/weather_observer.py"]