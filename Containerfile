FROM python:3.9-alpine as builder

WORKDIR /opt

ADD ["/src/", "/opt/"]
COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip
RUN apk update && apk add python3-dev \
                        gcc \
                        g++ \
                        libc-dev

RUN pip3 install --no-cache-dir -r requirements.txt

FROM builder

ENTRYPOINT ["python3", "/opt/weather_observer.py"]