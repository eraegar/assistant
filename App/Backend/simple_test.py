#!/usr/bin/env python3
import requests
import json

# Get token
response = requests.post('http://127.0.0.1:8000/api/v1/management/auth/login', json={'phone': '+79089050077', 'password': 'admin32451124'})
token = response.json()['access_token']
print(f'Token obtained: {token[:20]}...')

# Test basic clients endpoint
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://127.0.0.1:8000/api/v1/management/clients', headers=headers)
print(f'Basic clients: {response.status_code}')

if response.status_code != 200:
    print(f'Error: {response.text}')
else:
    data = response.json()
    print(f'Got {len(data["clients"])} clients')

# Test with subscription plan filter
print('\nTesting subscription plan filter...')
response = requests.get('http://127.0.0.1:8000/api/v1/management/clients?subscription_plan=full_8h', headers=headers)
print(f'Subscription filter: {response.status_code}')

if response.status_code != 200:
    print(f'Error: {response.text}')
else:
    data = response.json()
    print(f'Filtered clients: {len(data["clients"])}') 