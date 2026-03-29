import requests

url = "https://facebook-scraper3.p.rapidapi.com/page/page_id"
querystring = {"url": "https://www.facebook.com/Festivebreadke"}
posts = "https://facebook-scraper3.p.rapidapi.com/page/posts"


headers = {
    "x-rapidapi-key": "bd5904a96cmsh3edcc696733215fp1eeb5ajsne133bf560c27",
    "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
data = response.json()
response = requests.get(posts, headers=headers, params=data)

print(response.json())


