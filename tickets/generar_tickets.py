# tickets/generar_tickets.py
"""
Genera tickets de compra FALSOS (imágenes PNG) y fotos ilustrativas de productos
para probar el agente. Ejecutar:  Scripts\\python.exe tickets\\generar_tickets.py
"""
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
PRODUCTS_DIR = OUT / "productos"

TICKETS = [
    {
        "file": "ticket_soriana.png",
        "store": "SORIANA HIPER",
        "address": "Av. Universidad 1200, Ags.",
        "date": date.today() - timedelta(days=2),
        "items": [
            ("LECHE ENTERA LALA 1L", 2, 28.50),
            ("HUEVO BLANCO 12 PZ", 1, 54.90),
            ("JAMON DE PAVO FUD 250G", 1, 46.00),
            ("YOGURT NATURAL 1KG", 1, 39.90),
        ],
    },
    {
        "file": "ticket_walmart.png",
        "store": "WALMART SUPERCENTER",
        "address": "Blvd. Aguascalientes 4512",
        "date": date.today() - timedelta(days=5),
        "items": [
            ("POLLO PECHUGA KG", 1.2, 129.00),
            ("JITOMATE SALADET KG", 1.0, 32.00),
            ("LECHUGA ROMANA PZ", 1, 22.50),
            ("QUESO PANELA 400G", 1, 68.00),
            ("REFRESCO COLA 2L", 2, 36.00),
        ],
    },
    {
        "file": "ticket_oxxo.png",
        "store": "OXXO",
        "address": "Calle Madero 301, Centro",
        "date": date.today(),
        "items": [
            ("AGUA NATURAL 1.5L", 2, 17.00),
            ("MANTEQUILLA 90G", 1, 24.50),
            ("SANDWICH JAMON QUESO", 1, 42.00),
        ],
    },
]

# Foto ilustrativa por producto: (archivo, texto, color)
PRODUCTS = [
    ("leche.png", "LECHE", (235, 240, 250)),
    ("huevo.png", "HUEVO", (245, 225, 190)),
    ("jamon.png", "JAMON", (240, 170, 175)),
    ("yogurt.png", "YOGURT", (250, 250, 235)),
    ("pollo.png", "POLLO", (245, 205, 160)),
    ("jitomate.png", "JITOMATE", (225, 70, 60)),
    ("lechuga.png", "LECHUGA", (130, 200, 110)),
    ("queso.png", "QUESO", (250, 230, 140)),
    ("refresco.png", "REFRESCO", (120, 40, 30)),
    ("agua.png", "AGUA", (170, 215, 245)),
    ("mantequilla.png", "MANTEQUILLA", (250, 225, 120)),
    ("sandwich.png", "SANDWICH", (215, 175, 120)),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_ticket(ticket: dict) -> None:
    width, line_h = 520, 26
    lines = [
        ("c", ticket["store"], 26),
        ("c", ticket["address"], 16),
        ("c", "RFC: XAXX010101000", 16),
        ("l", "-" * 40, 16),
        ("l", f"FECHA: {ticket['date'].strftime('%d/%m/%Y')}   HORA: 18:42", 16),
        ("l", "CAJA: 04   TICKET: #" + str(sum(map(ord, ticket['file'])) * 397 % 900000 + 100000), 16),
        ("l", "-" * 40, 16),
        ("l", "CANT  DESCRIPCION              IMPORTE", 16),
    ]
    total = 0.0
    for name, qty, price in ticket["items"]:
        amount = qty * price
        total += amount
        lines.append(("l", f"{qty:<5} {name[:24]:<24} {amount:>8.2f}", 16))
    lines += [
        ("l", "-" * 40, 16),
        ("l", f"{'TOTAL':<31}${total:>8.2f}", 20),
        ("l", f"{'EFECTIVO':<31}${total + 50:>8.2f}", 16),
        ("l", f"{'CAMBIO':<31}${50:>8.2f}", 16),
        ("c", "", 16),
        ("c", "GRACIAS POR SU COMPRA", 18),
        ("c", "*** TICKET DE PRUEBA ***", 14),
    ]
    height = 40 + line_h * len(lines) + 20
    img = Image.new("RGB", (width, height), (252, 250, 243))
    d = ImageDraw.Draw(img)
    y = 30
    for align, text, size in lines:
        f = font(size)
        w = d.textlength(text, font=f)
        x = (width - w) / 2 if align == "c" else 24
        d.text((x, y), text, fill=(30, 30, 30), font=f)
        y += line_h
    # bordes dentados de papel térmico
    for x in range(0, width, 16):
        d.polygon([(x, 0), (x + 8, 10), (x + 16, 0)], fill=(220, 220, 220))
        d.polygon([(x, height), (x + 8, height - 10), (x + 16, height)], fill=(220, 220, 220))
    img.save(OUT / ticket["file"])


def draw_product(filename: str, label: str, color: tuple[int, int, int]) -> None:
    img = Image.new("RGB", (320, 320), (245, 245, 245))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 40, 280, 280), radius=36, fill=color, outline=(60, 60, 60), width=4)
    f = font(30 if len(label) < 9 else 24)
    w = d.textlength(label, font=f)
    text_color = (255, 255, 255) if sum(color) < 400 else (40, 40, 40)
    d.text(((320 - w) / 2, 145), label, fill=text_color, font=f)
    d.text((95, 290), "foto de prueba", fill=(120, 120, 120), font=font(16))
    img.save(PRODUCTS_DIR / filename)


if __name__ == "__main__":
    PRODUCTS_DIR.mkdir(exist_ok=True)
    for t in TICKETS:
        draw_ticket(t)
        print("ticket:", t["file"])
    for p in PRODUCTS:
        draw_product(*p)
    print(f"{len(PRODUCTS)} fotos de productos en {PRODUCTS_DIR}")
