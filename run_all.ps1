# --- run_all.ps1 (Windows PowerShell) ---

$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

$py  = Join-Path $root ".venv\Scripts\python.exe"
$act = Join-Path $root ".venv\Scripts\Activate.ps1"

function Start-Tab {
  param([string]$title,[string]$cmdBlock)
  Start-Process powershell -ArgumentList @('-NoExit','-NoLogo','-Command', $cmdBlock)
}

function NewBlock {
  param([string]$title,[string]$body)
@"
Write-Host '== $title ==' -ForegroundColor Cyan
Set-Location -LiteralPath "$root"
& "$act"
$body
"@
}

# ===== 1) MCPs =====
$calcBody = "& `"$py`" -m uvicorn server:app --app-dir `"$root\mcp_calc_server`"        --host 127.0.0.1 --port 8770"
$fligBody = "& `"$py`" -m uvicorn server:app --app-dir `"$root\mcp_flight_server`"      --host 127.0.0.1 --port 8771"
$hoteBody = "& `"$py`" -m uvicorn server:app --app-dir `"$root\mcp_hotel_server`"       --host 127.0.0.1 --port 8772"
$destBody = "& `"$py`" -m uvicorn server:app --app-dir `"$root\mcp_destination_server`" --host 127.0.0.1 --port 8773"

Start-Tab "MCP CALC (8770)"         (NewBlock "MCP CALC (8770)"         $calcBody)
Start-Tab "MCP FLIGHTS (8771)"      (NewBlock "MCP FLIGHTS (8771)"      $fligBody)
Start-Tab "MCP HOTELS (8772)"       (NewBlock "MCP HOTELS (8772)"       $hoteBody)
Start-Tab "MCP DESTINATIONS (8773)" (NewBlock "MCP DESTINATIONS (8773)" $destBody)

Start-Sleep -Seconds 3

# ===== 2) Backend =====
$backendBody = @"
`$env:CALC_SERVER_URL        = 'http://127.0.0.1:8770'
`$env:FLIGHT_SERVER_URL      = 'http://127.0.0.1:8771'
`$env:HOTEL_SERVER_URL       = 'http://127.0.0.1:8772'
`$env:DESTINATION_SERVER_URL = 'http://127.0.0.1:8773'
& `"$py`" -m uvicorn main:app --app-dir `"$root\backend`" --host 127.0.0.1 --port 8000
"@
Start-Tab "BACKEND (8000)" (NewBlock "BACKEND (8000)" $backendBody)

# ===== 3) Frontend =====
$frontendBody = @"
Set-Location -LiteralPath `"$root\frontend`"
npm run start
"@
Start-Tab "FRONTEND (3000)" (NewBlock "FRONTEND (3000)" $frontendBody)

# ===== 4) Chequeos rápidos =====
function Head200($url) {
  Try {
    $code = (curl.exe -s -o NUL -w '%{http_code}' $url)
    if ($code -eq '200') { Write-Host "✅ $url" -ForegroundColor Green } else { Write-Host "❌ $url -> $code" -ForegroundColor Red }
  } Catch { Write-Host "❌ $url (error)" -ForegroundColor Red }
}

Start-Sleep -Seconds 5
Head200 "http://127.0.0.1:8770/docs"
Head200 "http://127.0.0.1:8771/docs"
Head200 "http://127.0.0.1:8772/docs"
Head200 "http://127.0.0.1:8773/docs"
Head200 "http://127.0.0.1:8000/docs"
Head200 "http://127.0.0.1:3000"
