# weather_observer
Observe about the weather

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

API docs located is right here - https://www.weatherbit.io/api/weather-current

To execute program just pass the API key and get information in console. Or pass additional key `--file` and get report file.

### Example 

Regular usage:  
`weather_observer.exe --api-key YOUR_API_KEY`

If need report file:  
`weather_observer.exe --api-key YOUR_API_KEY --file`

If you want to get info only about you current location just pass `--local`:
`weather_observer.exe --api-key YOUR_API_KEY --local`

If you want to get more info about programm running pass `--verbosity` when using `--file`, 
have no sense while `--local` have been passed:
`weather_observer.exe --api-key YOUR_API_KEY --file --verbosity`

You also can wrap up invocation with `.sh` or `.bat`. Think about it.