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


To execute program just pass the API key and get information in console. Or pass additional key `--file` and get report file.

### Example 

Regular usage, will get cities from `cities.txt`, if not exist will create with current location city:  
`weather_observer.exe --api-key YOUR_API_KEY`

If need report to file:  
`weather_observer.exe --api-key YOUR_API_KEY --file`

If you want to get info only about you current location just pass `--local`:  
`weather_observer.exe --api-key YOUR_API_KEY --local`

If you want to get more info about programm running pass `--verbosity` when using `--file`, have no sense while `--local` have been passed:  
`weather_observer.exe --api-key YOUR_API_KEY --file --verbosity`

You also can wrap up invocation with `.sh` or `.bat`. Think about it.