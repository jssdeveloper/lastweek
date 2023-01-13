import requests
import random

def giphy(city):
    response = requests.get(f"https://api.giphy.com/v1/gifs/search?api_key=2AaDX0Ry3VMPqFuWZF8eQejKFCYbwjqP&q={city}&limit=25&offset=0&rating=g&lang=en").json()
    res = []
    for i in response["data"]:
        res.append(i["images"]["original"]["webp"])
    gifcount = len(res)
    randomgif = (random.randint(0,gifcount-1))
    return (res[randomgif])