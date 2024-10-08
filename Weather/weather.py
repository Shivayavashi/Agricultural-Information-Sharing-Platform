import requests

URL = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = "008a46fd637b639f0729c916f97220d7"
CITY = 'madurai'

url = URL + "appid=" + API_KEY + "&q=" + CITY
weather_data = requests.get(url).json()
weather_description = weather_data['weather'][0]['description']
temperature = weather_data['main']['temp']
humidity = weather_data['main']['humidity']
wind_speed = weather_data['wind']['speed']
print(weather_description,temperature,humidity,wind_speed)