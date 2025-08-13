import hashlib
import requests
from django.conf import settings

def digiflazz_signature(ref_id):
    text = settings.DIGIFLAZZ_USERNAME + settings.DIGIFLAZZ_API_KEY + ref_id
    return hashlib.md5(text.encode()).hexdigest()

def digiflazz_request(endpoint, payload):
    url = f"{settings.DIGIFLAZZ_BASE_URL}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
