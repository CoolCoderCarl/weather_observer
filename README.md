# weather_observer
Observe about the weather

Three APIs implemented:
1. https://www.weatherbit.io/api/weather-current
2. https://github.com/Jorl17/open-elevation/blob/master/docs/api.md
3. https://pygismeteo.readthedocs.io/ru/latest/

## Prehistory
I want to know more information about weather in countries ASAP.

> I like work with useful APIs  
> (c) Author

This program help to understand more about weather in any country around the world.

Enjoy.

## How to use
Preparation:  
For using this program the main thing you have to do it is to register here https://www.weatherbit.io/ and get API key.  
The second thing - download file `cities.txt` from repository.  
By the way, if you have no `cities.txt` file, it will create with your current location city name.

There are 5 ways to use this program:
1. Get current location and send report to console (default(just pass the API key))
2. Get current location and send report to file (`--output-file`)
3. Get cities from the file and send report to console (`--input-file`)
4. Get cities from the file and send report to file (`--input-file --output-file`)
5. Get current location and send report to telegram chat you specified (`--telegram`) or just run `docker-compose`

### Example 

Default usage:
`weather_observer.exe --api-key YOUR_API_KEY`

If need report to file:  
`weather_observer.exe --api-key YOUR_API_KEY --output-file`

If you want to get info about city or cities `--input-file`:  
`weather_observer.exe --api-key YOUR_API_KEY --input-file`

If you want to get more info about the program running pass `--verbosity` when using `--output-file`, have no sense while `--input-file` have been passed:  
`weather_observer.exe --api-key YOUR_API_KEY --output-file --verbosity`

You also can wrap up invocation with `.sh` or `.bat`. Think about it.