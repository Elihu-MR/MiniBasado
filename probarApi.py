# test_get_users.py
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1/users"

# === 1. Login para obtener el token ===
login_data = {
    "username": "elihu",       # cambia por tu usuario real
    "password": "elihu123" # cambia por tu contraseña real
}

login_response = requests.post(f"{BASE_URL}/token", data=login_data)

if login_response.status_code != 200:
    print(" Error al hacer login:", login_response.status_code, login_response.text)
    exit()

token = login_response.json()["access_token"]
print("Token obtenido:", token)

# === 2. Petición GET /users/ con el token ===
headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(f"{BASE_URL}/", headers=headers)

print("\nStatus code:", response.status_code)
print("Respuesta:")
print(response.json())