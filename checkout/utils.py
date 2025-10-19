import requests
from django.conf import settings

BASE = 'https://api.paystack.co'

def init_transaction(email: str, amount_kobo: int, reference: str, callback_url: str):
    url = f'{BASE}/transaction/initialize'
    headers = { 'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}' }
    data = {
        'email': email,
        'amount': amount_kobo,
        'reference': reference,
        'currency': settings.CURRENCY,
        'callback_url': callback_url,
    }
    r = requests.post(url, json=data, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

def verify_transaction(reference: str):
    url = f'{BASE}/transaction/verify/{reference}'
    headers = { 'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}' }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()
