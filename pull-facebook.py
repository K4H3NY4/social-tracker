import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
	"Authorization": "Bearer 3bb5d1d5-cff1-4c14-aacb-d441ebe63e58",
	"Content-Type": "application/json",
}
params = {
	"dataset_id": "gd_lkaxegm826bjpoo9m5",
	"endpoint": "https://0cae-217-21-114-58.ngrok-free.app/webhook",
	"auth_header": "3bb5d1d5-cff1-4c14-aacb-d441ebe63e58",
	"format": "json",
	"uncompressed_webhook": "true",
	"include_errors": "true",
}
data = [
	{"url":"https://www.facebook.com/LGEastAfrica","start_date":"01-01-2026","end_date":""},
	{"url":"https://www.facebook.com/BascoPaintsKenya","start_date":"01-01-2026","end_date":""},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())