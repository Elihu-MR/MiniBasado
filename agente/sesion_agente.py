# agente/sesion_agente.py
"""
Sesión del agente (Claude) registrada como script reproducible.

El agente leyó las imágenes de tickets/ (visión), extrajo los datos de abajo y
ejecutó estas llamadas a las herramientas del servidor FastMCP `mike-tickets`.
Cada llamada y su respuesta se guardan en agente/ejecucion_agente.log.

Uso:  Scripts\\python.exe agente\\sesion_agente.py
"""
import asyncio
import json
from pathlib import Path

from fastmcp import Client

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "agente" / "ejecucion_agente.log"

# Datos extraídos por el agente al leer cada ticket.
# expiration_date estimada con la vida útil típica del producto (el ticket no la trae).
TICKETS = [
    {
        "image_path": "ticket_soriana.png",
        "store_name": "Soriana Hiper",
        "purchase_date": "2026-10-12",
        "raw_text": "SORIANA HIPER - Av. Universidad 1200, Ags.\n2 LECHE ENTERA LALA 1L 57.00\n"
                    "1 HUEVO BLANCO 12 PZ 54.90\n1 JAMON DE PAVO FUD 250G 46.00\n"
                    "1 YOGURT NATURAL 1KG 39.90\nTOTAL $197.80",
        "items": [
            ("Leche entera Lala 1L", "Lácteos", 2, "L", 57.00, "2026-10-19", "productos/leche.png"),
            ("Huevo blanco 12 pz", "Huevo", 12, "pz", 54.90, "2026-11-02", "productos/huevo.png"),
            ("Jamón de pavo FUD 250g", "Carnes frías", 0.25, "kg", 46.00, "2026-10-19", "productos/jamon.png"),
            ("Yogurt natural 1kg", "Lácteos", 1, "kg", 39.90, "2026-10-26", "productos/yogurt.png"),
        ],
    },
    {
        "image_path": "ticket_walmart.png",
        "store_name": "Walmart Supercenter",
        "purchase_date": "2026-10-09",
        "raw_text": "WALMART SUPERCENTER - Blvd. Aguascalientes 4512\n1.2 POLLO PECHUGA KG 154.80\n"
                    "1.0 JITOMATE SALADET KG 32.00\n1 LECHUGA ROMANA PZ 22.50\n"
                    "1 QUESO PANELA 400G 68.00\n2 REFRESCO COLA 2L 72.00\nTOTAL $349.30",
        "items": [
            ("Pechuga de pollo", "Carnes", 1.2, "kg", 154.80, "2026-10-11", "productos/pollo.png"),
            ("Jitomate saladet", "Frutas y verduras", 1.0, "kg", 32.00, "2026-10-16", "productos/jitomate.png"),
            ("Lechuga romana", "Frutas y verduras", 1, "pz", 22.50, "2026-10-14", "productos/lechuga.png"),
            ("Queso panela 400g", "Lácteos", 0.4, "kg", 68.00, "2026-10-19", "productos/queso.png"),
            ("Refresco de cola 2L", "Bebidas", 4, "L", 72.00, "2027-04-07", "productos/refresco.png"),
        ],
    },
    {
        "image_path": "ticket_oxxo.png",
        "store_name": "OXXO",
        "purchase_date": "2026-10-14",
        "raw_text": "OXXO - Calle Madero 301, Centro\n2 AGUA NATURAL 1.5L 34.00\n"
                    "1 MANTEQUILLA 90G 24.50\n1 SANDWICH JAMON QUESO 42.00\nTOTAL $100.50",
        "items": [
            ("Agua natural 1.5L", "Bebidas", 3, "L", 34.00, "2027-10-14", "productos/agua.png"),
            ("Mantequilla 90g", "Lácteos", 0.09, "kg", 24.50, "2026-12-13", "productos/mantequilla.png"),
            ("Sándwich jamón y queso", "Preparados", 1, "pz", 42.00, "2026-10-16", "productos/sandwich.png"),
        ],
    },
]


async def main() -> None:
    log = LOG.open("w", encoding="utf-8")

    async def call(client: Client, tool: str, args: dict) -> dict:
        result = (await client.call_tool(tool, args)).data
        log.write(f">>> {tool}({json.dumps(args, ensure_ascii=False)})\n")
        log.write(json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n\n")
        print(f"[ok] {tool}")
        return result

    async with Client(ROOT / "mcp_server" / "server.py") as client:
        pending = await call(client, "listar_tickets_pendientes", {})
        fridge = await call(client, "obtener_o_crear_refrigerador", {})

        for t in TICKETS:
            if t["image_path"] not in pending["pendientes"]:
                print(f"[skip] {t['image_path']} ya registrado")
                continue
            ticket = await call(client, "registrar_ticket", {
                "refrigerator_id": fridge["id"],
                "image_path": t["image_path"],
                "store_name": t["store_name"],
                "purchase_date": t["purchase_date"],
                "raw_text": t["raw_text"],
            })
            for name, category, qty, unit, price, exp, photo in t["items"]:
                await call(client, "registrar_alimento", {
                    "ticket_id": ticket["id"],
                    "refrigerator_id": fridge["id"],
                    "name": name,
                    "category": category,
                    "quantity": qty,
                    "unit": unit,
                    "purchase_date": t["purchase_date"],
                    "expiration_date": exp,
                    "price": price,
                    "product_image_path": photo,
                })
            await call(client, "marcar_ticket_procesado", {"ticket_id": ticket["id"]})

        await call(client, "resumen_refrigerador", {"refrigerator_id": fridge["id"]})
    log.close()


if __name__ == "__main__":
    asyncio.run(main())
