import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
	"Authorization": "Bearer 3bb5d1d5-cff1-4c14-aacb-d441ebe63e58",
	"Content-Type": "application/json",
}
params = {
	"dataset_id": "gd_lk5ns7kz21pck8jpis",
	"endpoint": "https://0cae-217-21-114-58.ngrok-free.app/webhook",
	"auth_header": "3bb5d1d5-cff1-4c14-aacb-d441ebe63e58",
	"format": "json",
	"uncompressed_webhook": "true",
	"include_errors": "true",
	"type": "discover_new",
	"discover_by": "url",
}
data = [
	{"url":"https://www.instagram.com/lg_eastafrica/","start_date":"01-01-2026","end_date":"","post_type":""},
	{"url":"https://www.instagram.com/basco_paints/","start_date":"01-01-2026","end_date":"","post_type":""},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())