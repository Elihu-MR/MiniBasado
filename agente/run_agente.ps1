# agente/run_agente.ps1
# Ejecuta el agente (Claude Code en modo headless) conectado al servidor FastMCP.
# Requisitos: docker compose up -d  y  la API corriendo (uvicorn main:app --port 8000)
# Uso (desde la carpeta del proyecto):  .\agente\run_agente.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$prompt = Get-Content "$root\agente\prompt.md" -Raw -Encoding utf8
$log = "$root\agente\ejecucion_agente.log"

claude -p $prompt `
    --mcp-config "$root\.mcp.json" `
    --allowedTools "Read" "mcp__mike-tickets__*" `
    --output-format text | Tee-Object -FilePath $log
