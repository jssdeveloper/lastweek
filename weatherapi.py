import requests

def get_weather(city_name):
	API_key = "0951ebb00319e01258d421af9baa3d0c"
	url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={API_key}"
	response = requests.get(url)
	code = response.json()["cod"]
	
	if code == 200:
		country = (response.json()['sys']['country'])
		weather = response.json()['weather'][0]['main']
		temperature = round(response.json()['main']['temp'])
		return temperature
	else:
		return("error")