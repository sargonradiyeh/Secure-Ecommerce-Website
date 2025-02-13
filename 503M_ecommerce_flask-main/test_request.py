# test_request.py

import requests
import os

CA_CERT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", "ca.crt")
RBAC_SERVICE_URL = 'https://localhost:5001/api/login'

data = {
    'username': 'admin',
    'password': 'admin123'
}

try:
    response = requests.post(
        RBAC_SERVICE_URL,
        json=data,
        verify=CA_CERT_PATH,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.SSLError as e:
    print(f"SSL Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request Exception: {e}")