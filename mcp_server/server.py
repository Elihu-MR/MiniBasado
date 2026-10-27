# mcp_server/server.py
"""
Servidor MCP (FastMCP) que expone la API de Mike y el almacenamiento MinIO
como herramientas para un agente de IA.

El agente lee la imagen de un ticket de compra, extrae tienda, fecha y
productos, y usa estas herramientas para:
  1. Subir la imagen del ticket a MinIO y registrar el PurchaseTicket.
  2. Registrar cada producto como Food en el refrigerador.
  3. Subir la foto de cada producto a MinIO y registrar sus FoodImage.
  4. Marcar el ticket como procesado.

Ejecutar (stdio):   Scripts\\python.exe mcp_server\\server.py
"""
import mimetypes
import os
import sys
import uuid
from datetime import date
from pathlib import Path
from typing import Any

import boto3
import httpx
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastmcp import FastMCP

PROJECT_DIR = Path(__file__).resolve().parent.parent
TICKETS_DIR = PROJECT_DIR / "tickets"

load_dotenv(PROJECT_DIR / ".env")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")
API_USER = os.getenv("MCP_API_USER", "")
API_PASSWORD = os.getenv("MCP_API_PASSWORD", "")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_BUCKET = os.getenv("MINIO_BUCKET_NAME", "fastapi-images")

# Días antes de caducar en los que un alimento se considera "expiring"
EXPIRING_DAYS = 3

mcp = FastMCP(
    name="mike-tickets",
    instructions=(
        "Herramientas para poblar la API de Mike (refrigerador inteligente) a partir de "
        "tickets de compra. Flujo: listar_tickets_pendientes -> leer la imagen del ticket -> "
        "obtener_o_crear_refrigerador -> registrar_ticket -> registrar_alimento por cada "
        "producto -> marcar_ticket_procesado."
    ),
)


# === Utilidades internas ===

class ApiClient:
    """Cliente HTTP con login JWT automático contra la API."""

    def __init__(self) -> None:
        self._token: str | None = None
        self._user_id: int | None = None
        self._http = httpx.Client(base_url=API_URL, timeout=20)

    def _login(self) -> None:
        response = self._http.post("/token", data={"username": API_USER, "password": API_PASSWORD})
        response.raise_for_status()
        self._token = response.json()["access_token"]

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        if self._token is None:
            self._login()
        headers = {"Authorization": f"Bearer {self._token}"}
        response = self._http.request(method, path, headers=headers, **kwargs)
        if response.status_code == 401:  # token expirado
            self._login()
            headers = {"Authorization": f"Bearer {self._token}"}
            response = self._http.request(method, path, headers=headers, **kwargs)
        if response.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {response.status_code}: {response.text}")
        return response.json() if response.content else None

    @property
    def user_id(self) -> int:
        if self._user_id is None:
            users = self.request("GET", "/")
            match = next((u for u in users if u["username"] == API_USER), None)
            if match is None:
                raise RuntimeError(f"No se encontró el usuario {API_USER}")
            self._user_id = match["id"]
        return self._user_id


api = ApiClient()

minio = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "admin"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "admin123"),
    config=Config(signature_version="s3v4"),
    region_name=os.getenv("MINIO_REGION", "us-east-1"),
)


def _ensure_bucket() -> None:
    try:
        minio.head_bucket(Bucket=MINIO_BUCKET)
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
            minio.create_bucket(Bucket=MINIO_BUCKET)
        else:
            raise


def _resolve_image(image_path: str) -> Path:
    """Acepta rutas relativas a la carpeta tickets/ o al proyecto."""
    for candidate in (Path(image_path), TICKETS_DIR / image_path, PROJECT_DIR / image_path):
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(f"No existe la imagen: {image_path}")


def _upload(image_path: str, folder: str) -> str:
    """Sube un archivo local a MinIO y devuelve su URL."""
    path = _resolve_image(image_path)
    _ensure_bucket()
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    key = f"{folder}/{uuid.uuid4().hex}{path.suffix.lower()}"
    minio.upload_file(str(path), MINIO_BUCKET, key, ExtraArgs={"ContentType": content_type})
    return f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{key}"


def _food_status(expiration_date: date) -> str:
    days_left = (expiration_date - date.today()).days
    if days_left < 0:
        return "expired"
    if days_left <= EXPIRING_DAYS:
        return "expiring"
    return "fresh"


# === Herramientas MCP ===

@mcp.tool
def listar_tickets_pendientes() -> dict[str, Any]:
    """Lista las imágenes de tickets en la carpeta tickets/ que aún no se han registrado
    en la API, junto con las fotos de productos disponibles en tickets/productos/."""
    registered = {
        t["raw_text"].split("\n", 1)[0].removeprefix("archivo: ")
        for t in api.request("GET", "/purchase-tickets/", params={"limit": 500})
        if (t.get("raw_text") or "").startswith("archivo: ")
    }
    tickets = sorted(p.name for p in TICKETS_DIR.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
    products = sorted(p.name for p in (TICKETS_DIR / "productos").glob("*") if p.is_file())
    return {
        "carpeta": str(TICKETS_DIR),
        "pendientes": [t for t in tickets if t not in registered],
        "ya_registrados": [t for t in tickets if t in registered],
        "fotos_de_productos": [f"productos/{p}" for p in products],
    }


@mcp.tool
def obtener_o_crear_refrigerador(
    name: str = "Refrigerador principal",
    brand: str = "Mabe",
    capacity_liters: int = 400,
) -> dict[str, Any]:
    """Devuelve el refrigerador del usuario con ese nombre; si no existe, lo crea."""
    fridges = api.request("GET", "/refrigerators/", params={"limit": 500})
    for fridge in fridges:
        if fridge["user_id"] == api.user_id and fridge["name"] == name:
            return fridge
    return api.request("POST", "/refrigerators/", json={
        "user_id": api.user_id,
        "name": name,
        "brand": brand,
        "esp32_device_id": f"esp32-{uuid.uuid4().hex[:8]}",
        "capacity_liters": capacity_liters,
        "is_active": True,
    })


@mcp.tool
def registrar_ticket(
    refrigerator_id: int,
    image_path: str,
    store_name: str,
    purchase_date: date,
    raw_text: str,
) -> dict[str, Any]:
    """Sube la imagen del ticket a MinIO y crea el PurchaseTicket en la API.

    image_path: nombre del archivo dentro de tickets/ (ej. 'ticket_soriana.png').
    raw_text: texto transcrito del ticket (productos, precios, total).
    """
    url = _upload(image_path, "tickets")
    return api.request("POST", "/purchase-tickets/", json={
        "user_id": api.user_id,
        "refrigerator_id": refrigerator_id,
        "store_name": store_name,
        "purchase_date": purchase_date.isoformat(),
        "ticket_image_url": url,
        "raw_text": f"archivo: {Path(image_path).name}\n{raw_text}",
        "processed_at": False,
    })


@mcp.tool
def registrar_alimento(
    ticket_id: int,
    refrigerator_id: int,
    name: str,
    category: str,
    quantity: float,
    unit: str,
    purchase_date: date,
    expiration_date: date,
    price: float | None = None,
    product_image_path: str | None = None,
) -> dict[str, Any]:
    """Registra un producto del ticket como Food y guarda sus imágenes.

    - Crea el Food (el status fresh/expiring/expired se calcula con la fecha de caducidad).
    - Vincula la imagen del ticket como FoodImage tipo 'ticket'.
    - Si se da product_image_path (ej. 'productos/leche.png'), la sube a MinIO
      y la registra como FoodImage tipo 'food'.
    expiration_date: si el ticket no la trae, estímala según el tipo de producto.
    """
    ticket = api.request("GET", f"/purchase-tickets/{ticket_id}")
    food = api.request("POST", "/foods/", json={
        "refrigerator_id": refrigerator_id,
        "name": name,
        "category": category,
        "quantity": quantity,
        "unit": unit,
        "purchase_date": purchase_date.isoformat(),
        "expiration_date": expiration_date.isoformat(),
        "status": _food_status(expiration_date),
    })
    analysis = {"price": price, "store": ticket["store_name"], "source": "agente-mcp"}

    images = [api.request("POST", "/food-images/", json={
        "food_id": food["id"],
        "ticket_id": ticket_id,
        "image_url": ticket["ticket_image_url"],
        "image_type": "ticket",
        "ocr_extracted_text": f"{name} x{quantity} {unit}" + (f" ${price:.2f}" if price is not None else ""),
        "ai_analysis": analysis,
    })]
    if product_image_path:
        images.append(api.request("POST", "/food-images/", json={
            "food_id": food["id"],
            "ticket_id": ticket_id,
            "image_url": _upload(product_image_path, "foods"),
            "image_type": "food",
            "ai_analysis": analysis,
        }))
    return {"food": food, "images": images}


@mcp.tool
def subir_imagen(image_path: str, folder: str = "otros") -> dict[str, Any]:
    """Sube cualquier imagen a MinIO sin registrarla en la API.

    image_path: ruta dentro de tickets/ (ej. 'otros/hola_mundo.png').
    folder: carpeta del bucket donde se guarda (por defecto 'otros').
    """
    url = _upload(image_path, folder)
    return {"bucket": MINIO_BUCKET, "url": url, "key": url.split(f"/{MINIO_BUCKET}/", 1)[1]}


@mcp.tool
def marcar_ticket_procesado(ticket_id: int) -> dict[str, Any]:
    """Marca el ticket como procesado cuando ya se registraron todos sus productos."""
    return api.request("PUT", f"/purchase-tickets/{ticket_id}", json={"processed_at": True})


@mcp.tool
def resumen_refrigerador(refrigerator_id: int) -> dict[str, Any]:
    """Devuelve los tickets, alimentos e imágenes registrados para un refrigerador."""
    tickets = [t for t in api.request("GET", "/purchase-tickets/", params={"limit": 500})
               if t["refrigerator_id"] == refrigerator_id]
    foods = [f for f in api.request("GET", "/foods/", params={"limit": 500})
             if f["refrigerator_id"] == refrigerator_id]
    food_ids = {f["id"] for f in foods}
    images = [i for i in api.request("GET", "/food-images/", params={"limit": 500})
              if i["food_id"] in food_ids]
    return {
        "tickets": [{k: t[k] for k in ("id", "store_name", "purchase_date", "processed_at")} for t in tickets],
        "alimentos": [{k: f[k] for k in ("id", "name", "quantity", "unit", "expiration_date", "status")} for f in foods],
        "total_imagenes": len(images),
    }


if __name__ == "__main__":
    print(f"mike-tickets MCP -> API {API_URL}, MinIO {MINIO_ENDPOINT}/{MINIO_BUCKET}", file=sys.stderr)
    mcp.run()
