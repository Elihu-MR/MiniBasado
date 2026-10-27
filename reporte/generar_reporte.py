# reporte/generar_reporte.py
"""
Genera reporte/Reporte_Integracion_APIs_Agente.pdf con los datos reales de la API.
Requisitos: API corriendo en :8000. Usa Microsoft Edge (headless) para exportar el PDF.
Uso:  Scripts\\python.exe reporte\\generar_reporte.py
"""
import base64
import html
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "reporte"
API = "http://127.0.0.1:8000/api/v1"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def img64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def esc(value) -> str:
    return html.escape(str(value))


tickets = requests.get(f"{API}/purchase-tickets/").json()
foods = requests.get(f"{API}/foods/").json()
images = requests.get(f"{API}/food-images/").json()
fridges = requests.get(f"{API}/refrigerators/").json()
status_count = Counter(f["status"] for f in foods)
image_count = Counter(i["image_type"] for i in images)
ticket_by_food = {i["food_id"]: i["ticket_id"] for i in images}
store_by_ticket = {t["id"]: t["store_name"] for t in tickets}
price_by_food = {i["food_id"]: (i.get("ai_analysis") or {}).get("price") for i in images}

ticket_rows = "".join(
    f"<tr><td>{t['id']}</td><td>{esc(t['store_name'])}</td><td class='nw'>{t['purchase_date']}</td>"
    f"<td>{'Sí' if t['processed_at'] else 'No'}</td><td class='mono'>{esc(t['ticket_image_url'].split('/', 3)[-1])}</td></tr>"
    for t in tickets
)
STATUS_ES = {"fresh": "fresco", "expiring": "por caducar", "expired": "caducado", "consumed": "consumido"}
food_rows = "".join(
    f"<tr><td>{f['id']}</td><td>{esc(f['name'])}</td><td>{esc(f['category'])}</td>"
    f"<td>{float(f['quantity']):g} {esc(f['unit'])}</td>"
    f"<td>${price_by_food.get(f['id']) or 0:.2f}</td>"
    f"<td>{esc(store_by_ticket.get(ticket_by_food.get(f['id']), ''))}</td>"
    f"<td class='nw'>{f['expiration_date']}</td><td class='nw'><span class='st {f['status']}'>{STATUS_ES[f['status']]}</span></td></tr>"
    for f in foods
)
ticket_imgs = "".join(
    f"<figure><img src='{img64(ROOT / 'tickets' / n)}'><figcaption>{n}</figcaption></figure>"
    for n in ("ticket_soriana.png", "ticket_walmart.png", "ticket_oxxo.png")
)
product_imgs = "".join(
    f"<img src='{img64(p)}' title='{p.name}'>" for p in sorted((ROOT / "tickets" / "productos").glob("*.png"))
)

log_lines = (ROOT / "agente" / "ejecucion_agente.log").read_text(encoding="utf-8").split("\n")
log_excerpt = esc("\n".join(log_lines[:34]))

server_code = (ROOT / "mcp_server" / "server.py").read_text(encoding="utf-8")
tool_snippet = server_code[server_code.index("@mcp.tool\ndef registrar_ticket"):server_code.index("@mcp.tool\ndef registrar_alimento")]

ARCH_SVG = """
<svg viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="13">
  <defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0,0 L10,5 L0,10 z" fill="#334"/></marker></defs>
  <g fill="#fff" stroke="#334" stroke-width="1.5">
    <rect x="10" y="90" width="120" height="60" rx="8" fill="#fdf6e3"/>
    <rect x="180" y="90" width="140" height="60" rx="8" fill="#e8eefc"/>
    <rect x="370" y="90" width="150" height="60" rx="8" fill="#e6f4ea"/>
    <rect x="580" y="20" width="160" height="60" rx="8" fill="#fde8e8"/>
    <rect x="580" y="160" width="160" height="60" rx="8" fill="#f1e8fd"/>
    <rect x="370" y="190" width="150" height="45" rx="8" fill="#f5f5f5"/>
  </g>
  <g text-anchor="middle" fill="#123">
    <text x="70" y="115" font-weight="600">Tickets</text><text x="70" y="133">imágenes PNG/JPG</text>
    <text x="250" y="115" font-weight="600">Agente (Claude)</text><text x="250" y="133">visión + razonamiento</text>
    <text x="445" y="115" font-weight="600">Servidor FastMCP</text><text x="445" y="133">mike-tickets (stdio)</text>
    <text x="660" y="45" font-weight="600">API FastAPI</text><text x="660" y="63">JWT · /api/v1</text>
    <text x="660" y="185" font-weight="600">MinIO (S3)</text><text x="660" y="203">bucket fastapi-images</text>
    <text x="445" y="218">PostgreSQL</text>
  </g>
  <g stroke="#334" stroke-width="1.5" marker-end="url(#a)" fill="none">
    <line x1="130" y1="120" x2="178" y2="120"/>
    <line x1="320" y1="120" x2="368" y2="120"/>
    <line x1="520" y1="110" x2="578" y2="60"/>
    <line x1="520" y1="130" x2="578" y2="180"/>
    <line x1="600" y1="80" x2="500" y2="190"/>
  </g>
  <g font-size="11" fill="#556" text-anchor="middle">
    <text x="154" y="110">lee</text><text x="344" y="110">MCP</text>
    <text x="560" y="78">HTTP</text><text x="560" y="170">boto3</text><text x="565" y="140">SQL</text>
  </g>
</svg>"""

HTML = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Integración de APIs con Agente</title>
<style>
@page {{ size: Letter; margin: 18mm 16mm; }}
body {{ font-family: 'Segoe UI', Arial, sans-serif; color:#1d2433; font-size:11pt; line-height:1.5; }}
h1 {{ font-size:26pt; margin:0 0 6px; color:#16325c; }}
h2 {{ font-size:16pt; color:#16325c; border-bottom:2px solid #16325c; padding-bottom:3px; margin-top:26px; }}
h3 {{ font-size:12.5pt; color:#24477a; margin:18px 0 6px; }}
.cover {{ height:230mm; display:flex; flex-direction:column; justify-content:center; page-break-after:always; }}
.cover .sub {{ font-size:14pt; color:#4a5878; margin-bottom:40px; }}
.cover .meta {{ font-size:11.5pt; color:#333; border-left:4px solid #16325c; padding-left:12px; }}
.cover .meta div {{ margin:4px 0; }}
table {{ width:100%; border-collapse:collapse; font-size:9.5pt; margin:8px 0 14px; }}
th {{ background:#16325c; color:#fff; text-align:left; padding:5px 6px; }}
td.nw {{ white-space:nowrap; }}
td {{ border-bottom:1px solid #dde2ec; padding:4px 6px; }}
tr:nth-child(even) td {{ background:#f6f8fc; }}
.mono, pre, code {{ font-family:Consolas, monospace; font-size:8.6pt; }}
pre {{ background:#f4f6fa; border:1px solid #dde2ec; border-radius:6px; padding:10px; white-space:pre-wrap; }}
.tickets {{ display:flex; gap:10px; justify-content:space-between; }}
.tickets figure {{ margin:0; width:32%; text-align:center; font-size:9pt; color:#556; }}
.tickets img {{ width:100%; border:1px solid #ccd; }}
.products img {{ width:62px; margin:3px; border:1px solid #ccd; border-radius:6px; }}
.kpis {{ display:flex; gap:10px; margin:10px 0; }}
.kpi {{ flex:1; border:1px solid #dde2ec; border-radius:8px; padding:8px; text-align:center; }}
.kpi b {{ display:block; font-size:20pt; color:#16325c; }}
.st {{ padding:1px 7px; border-radius:9px; font-size:8.5pt; }}
.st.fresh {{ background:#e1f3e5; color:#1d6b33; }} .st.expiring {{ background:#fff1d0; color:#8a5a00; }}
.st.expired {{ background:#fde0e0; color:#a12626; }}
.avoid {{ page-break-inside:avoid; }}
</style></head><body>

<section class="cover">
  <h1>Integración de APIs con Agente</h1>
  <div class="sub">Poblado automático de la API del refrigerador inteligente "Mike" a partir de tickets de compra usando MinIO, FastMCP y un agente de IA</div>
  <div class="meta">
    <div><b>Alumno:</b> ______________________________</div>
    <div><b>Materia:</b> ______________________________</div>
    <div><b>Profesor:</b> ______________________________</div>
    <div><b>Fecha:</b> {date.today().strftime('%d/%m/%Y')}</div>
  </div>
</section>

<h2>1. Introducción</h2>
<p>El proyecto <b>Mike API</b> es un backend en FastAPI para un refrigerador inteligente: gestiona usuarios, refrigeradores,
alimentos, tickets de compra, imágenes, sensores y cámaras, con persistencia en PostgreSQL y archivos en MinIO.
Capturar a mano cada producto comprado es lento y propenso a errores, así que esta actividad automatiza el registro:
un <b>agente de IA</b> lee la foto de un ticket, interpreta su contenido y llena las APIs con los datos y las imágenes correspondientes.</p>
<p>Para que el agente pueda actuar sobre el sistema se construyó un <b>servidor MCP</b> (Model Context Protocol) con la librería
<b>FastMCP</b>. Este servidor expone herramientas bien definidas que encapsulan la autenticación JWT, las llamadas HTTP a la API
y la subida de archivos a <b>MinIO</b>, un almacenamiento de objetos compatible con Amazon S3.</p>
<p><b>Objetivos:</b></p>
<ul>
  <li>Exponer las APIs de tickets, alimentos e imágenes como herramientas MCP reutilizables por cualquier agente.</li>
  <li>Guardar las imágenes de los tickets y de los productos en MinIO y referenciarlas desde la base de datos.</li>
  <li>Hacer que el agente procese tickets de prueba de principio a fin, sin capturar datos a mano.</li>
</ul>

<h2>2. Desarrollo</h2>
<h3>2.1 Arquitectura</h3>
<div class="avoid">{ARCH_SVG}</div>
<p>El agente nunca habla directamente con la base de datos ni con MinIO: todo pasa por las herramientas del servidor MCP.
El servidor inicia sesión en la API con un usuario de servicio (<code>MCP_API_USER</code> en <code>.env</code>), renueva el token
si expira y usa <code>boto3</code> para subir archivos al bucket <code>{esc('fastapi-images')}</code>.</p>

<h3>2.2 Infraestructura</h3>
<ul>
  <li><b>PostgreSQL 15</b> y <b>MinIO</b> levantados con <code>docker compose up -d</code> (puertos 5433, 9000 y 9001).</li>
  <li><b>API FastAPI</b> con <code>uvicorn main:app --port 8000</code>; rutas bajo <code>/api/v1</code>.</li>
  <li>Entorno virtual de Python 3.14 con <code>fastmcp 4.1</code>, <code>boto3</code>, <code>httpx</code> y <code>Pillow</code>.</li>
</ul>

<h3>2.3 Servidor FastMCP (<code>mcp_server/server.py</code>)</h3>
<table>
  <tr><th>Herramienta</th><th>Qué hace</th><th>API / servicio</th></tr>
  <tr><td>listar_tickets_pendientes</td><td>Lista los tickets en <code>tickets/</code> que aún no están registrados y las fotos de productos</td><td>GET /purchase-tickets</td></tr>
  <tr><td>obtener_o_crear_refrigerador</td><td>Busca o crea el refrigerador del usuario</td><td>GET/POST /refrigerators</td></tr>
  <tr><td>registrar_ticket</td><td>Sube la imagen del ticket a MinIO y crea el PurchaseTicket</td><td>MinIO + POST /purchase-tickets</td></tr>
  <tr><td>registrar_alimento</td><td>Crea el Food (calcula fresco, por caducar o caducado), vincula la imagen del ticket y sube la foto del producto</td><td>POST /foods, MinIO + POST /food-images</td></tr>
  <tr><td>marcar_ticket_procesado</td><td>Marca el ticket como procesado</td><td>PUT /purchase-tickets/{{id}}</td></tr>
  <tr><td>resumen_refrigerador</td><td>Resume los tickets, alimentos e imágenes registrados</td><td>GET (varios)</td></tr>
</table>
<p>Ejemplo de herramienta: FastMCP genera el esquema de entrada a partir de los <i>type hints</i> y el docstring se convierte en la descripción que lee el agente.</p>
<pre>{esc(tool_snippet.strip())}</pre>
<p>El servidor se registra para el agente en <code>.mcp.json</code>, así Claude Code lo carga automáticamente al abrir el proyecto.</p>

<h3>2.4 Tickets de prueba</h3>
<p>Con <code>tickets/generar_tickets.py</code> (Pillow) se generaron tres tickets falsos de tiendas distintas y doce fotos ilustrativas de productos.</p>
<div class="tickets avoid">{ticket_imgs}</div>
<div class="products avoid">{product_imgs}</div>

<h3>2.5 El agente</h3>
<p>El agente es <b>Claude</b> conectado al servidor MCP. Las instrucciones están en <code>agente/prompt.md</code>:</p>
<ol>
  <li>Consulta los tickets pendientes y obtiene el refrigerador.</li>
  <li>Abre cada imagen y extrae, con visión, la tienda, la fecha y los productos con cantidad, unidad e importe.</li>
  <li>Normaliza los datos: nombre legible, categoría, unidad (kg, L o pz) y la fecha en formato ISO.</li>
  <li>Como los tickets no traen fecha de caducidad, la estima con la vida útil típica de cada producto.</li>
  <li>Registra el ticket, cada alimento con sus imágenes, y marca el ticket como procesado.</li>
</ol>
<p>Se ejecuta con <code>agente\\run_agente.ps1</code> (Claude Code en modo headless con <code>--mcp-config .mcp.json</code>).
La sesión ejecutada también quedó como script reproducible en <code>agente/sesion_agente.py</code>, y cada llamada a herramienta
con su respuesta se registró en <code>agente/ejecucion_agente.log</code>. Extracto:</p>
<pre>{log_excerpt}
...</pre>

<h3>2.6 Resultados</h3>
<div class="kpis">
  <div class="kpi"><b>{len(fridges)}</b>refrigerador</div>
  <div class="kpi"><b>{len(tickets)}</b>tickets</div>
  <div class="kpi"><b>{len(foods)}</b>alimentos</div>
  <div class="kpi"><b>{len(images)}</b>imágenes ({image_count['ticket']} de ticket, {image_count['food']} de producto)</div>
</div>
<div class="avoid">
<p><b>Tickets registrados</b> (la imagen se guardó en MinIO):</p>
<table><tr><th>ID</th><th>Tienda</th><th>Fecha</th><th>Procesado</th><th>Objeto en MinIO</th></tr>{ticket_rows}</table>
</div>
<p><b>Alimentos registrados por el agente:</b></p>
<table><tr><th>ID</th><th>Alimento</th><th>Categoría</th><th>Cantidad</th><th>Importe</th><th>Tienda</th><th>Caduca</th><th>Estado</th></tr>{food_rows}</table>
<p>Estados al {date.today().strftime('%d/%m/%Y')}: {status_count['fresh']} frescos, {status_count['expiring']} por caducar y
{status_count['expired']} caducado. La pechuga de pollo, comprada el 09/10, ya superó los 2 días de vida útil en refrigeración.</p>

<div class="avoid"><h2>3. Conclusión</h2>
<p>La integración cumplió su objetivo: a partir de tres imágenes de tickets, el agente registró de forma autónoma
{len(tickets)} tickets, {len(foods)} alimentos y {len(images)} imágenes de alimentos. Además, guardó 15 archivos en MinIO: los 3 tickets
y las 12 fotos de productos. Nadie tuvo que capturar datos a mano: el agente interpretó texto no estructurado, lo normalizó
y decidió qué herramienta usar en cada paso.</p></div>
<p>El servidor MCP fue la pieza clave: separa la lógica de negocio y las credenciales del modelo de IA. El agente solo
conoce herramientas con nombres, parámetros tipados y descripciones claras, mientras que la autenticación JWT, las URLs
y el acceso a MinIO quedan del lado del servidor. Esto hace al sistema más seguro y fácil de mantener. Además, el mismo servidor
puede usarse con otros clientes compatibles con MCP.</p>
<p><b>Mejoras posibles:</b> leer la fecha de caducidad desde fotos de las etiquetas; agregar un endpoint de subida de
imágenes a la API para no acceder a MinIO desde el servidor MCP; usar URLs firmadas para mostrar las imágenes al cliente;
y procesar tickets reales automáticamente cuando se suban desde la app o desde la cámara del ESP32.</p>
</body></html>"""

OUT_DIR.mkdir(exist_ok=True)
html_path = OUT_DIR / "reporte.html"
pdf_path = OUT_DIR / "Reporte_Integracion_APIs_Agente.pdf"
html_path.write_text(HTML, encoding="utf-8")
subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}", html_path.as_uri()], check=True, timeout=120)
print("PDF:", pdf_path)
