import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
	"Authorization": "Bearer 3bb5d1d5-cff1-4c14-aacb-d441ebe63e58",
	"Content-Type": "application/json",
}
params = {
	"dataset_id": "gd_m7n5v2gq296pex2f5m",
	"include_errors": "true",
}
data = [
	{"url":"https://www.tiktok.com/@lg_eastafrica"},
	{"url":"https://www.tiktok.com/@bascopaintskenya"},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())