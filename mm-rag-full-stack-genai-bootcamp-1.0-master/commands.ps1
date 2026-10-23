# =====================================================================
# MM-RAG - startup / shutdown / diagnostics
#
#   .\commands.ps1 doctor     diagnose interpreters, containers, ports
#   .\commands.ps1 start      start the stack natively, using .venv
#   .\commands.ps1 stop       stop the natively started processes
#   .\commands.ps1 status     health check every dependency
#   .\commands.ps1 init-db    create the PostgreSQL schema (idempotent)
#
#   .\commands.ps1 up         docker compose up -d --build
#   .\commands.ps1 down       docker compose down   (never passes -v)
#   .\commands.ps1 ps         docker compose ps
#   .\commands.ps1 logs       docker compose logs -f --tail=100
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# `where python` on this machine resolves to Python 3.14 - a *second* complete
# CPython install with its own torch, its own c10.dll and its own copy of the
# MSVC runtime. Launching any part of this project with bare `python` therefore
# loads a different native stack than the pinned .venv (Python 3.11), and
# Windows kills the process with 0xc0000005 STATUS_ACCESS_VIOLATION - no Python
# traceback, no log line.
#
# Every command below resolves .venv\Scripts\python.exe by absolute path and
# verifies it is really Python 3.11 before starting anything.
# =====================================================================

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('doctor', 'start', 'stop', 'status', 'init-db',
                 'up', 'down', 'ps', 'logs')]
    [string]$Action = 'status'
)

$ErrorActionPreference = 'Stop'

$Root     = $PSScriptRoot
Set-Location -LiteralPath $Root

$VenvPy   = Join-Path $Root '.venv\Scripts\python.exe'
$RunDir   = Join-Path $Root 'data\run'
$LogDir   = Join-Path $Root 'logs'
$Expected = '3.11'
$ApiUrl   = 'http://127.0.0.1:8000'
$UiUrl    = 'http://127.0.0.1:8502'

# ---------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------

function Write-Head([string]$Text) {
    $pad = [Math]::Max(0, 60 - $Text.Length)
    Write-Host ''
    Write-Host "== $Text " -ForegroundColor Cyan -NoNewline
    Write-Host ('=' * $pad) -ForegroundColor Cyan
}
function Write-Ok([string]$Text)   { Write-Host "  [ OK ]  $Text" -ForegroundColor Green }
function Write-Warn([string]$Text) { Write-Host "  [WARN]  $Text" -ForegroundColor Yellow }
function Write-Bad([string]$Text)  { Write-Host "  [FAIL]  $Text" -ForegroundColor Red }
function Write-Info([string]$Text) { Write-Host "          $Text" -ForegroundColor DarkGray }

# ---------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------

function Get-VenvPython {
    if (-not (Test-Path -LiteralPath $VenvPy)) {
        throw "Pinned interpreter not found at $VenvPy"
    }
    return $VenvPy
}

# Verifies the interpreter really is the one the project was built against.
# Deliberately cheap - it does not import torch, so it is safe to run before
# every launch.
function Assert-Interpreter {
    $py = Get-VenvPython
    $lines = @(& $py -c "import sys; print('.'.join(map(str, sys.version_info[:2]))); print(sys.executable)")
    if ($LASTEXITCODE -ne 0) { throw "Interpreter $py failed to start (exit $LASTEXITCODE)." }

    $ver = [string]$lines[-2]
    $exe = [string]$lines[-1]

    if (-not $ver.Trim().StartsWith($Expected)) {
        throw "Interpreter is $($ver.Trim()), expected $Expected. Refusing to start - this is the 0xc0000005 cause."
    }
    if (-not $exe.Trim().ToLower().StartsWith($Root.ToLower())) {
        throw "sys.executable is '$($exe.Trim())', which is outside the project .venv. Refusing to start."
    }
    return $py
}

function Test-Url([string]$Url) {
    try {
        $r = Invoke-WebRequest -Uri $Url -TimeoutSec 5 -UseBasicParsing
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400)
    } catch {
        return $false
    }
}

function Test-Port([int]$Port) {
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $c.Connect('127.0.0.1', $Port)
        $c.Close()
        return $true
    } catch {
        return $false
    }
}

function Get-ContainerState([string]$Name) {
    $s = @(& docker inspect -f '{{.State.Status}}' $Name 2>$null)
    if ($LASTEXITCODE -ne 0 -or $s.Count -eq 0) { return $null }
    return ([string]$s[0]).Trim()
}

# Free physical RAM in GB. Generation needs headroom: when llama3.2:1b cannot
# get its ~1.3 GB CPU buffer, Ollama returns HTTP 500 and /query fails with
# "failed to allocate buffer" even though retrieval succeeded. Measured on this
# machine: 0.6 GB free -> query failed; 1.7 GB free -> query passed in 22 s.
function Get-FreeRamGb {
    $os = Get-CimInstance Win32_OperatingSystem
    return [math]::Round($os.FreePhysicalMemory / 1MB, 2)
}

function Show-OllamaModels {
    try {
        $r = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5
        $names = @($r.models | ForEach-Object { $_.name })
        Write-Ok "Ollama reachable on 11434 ($($names.Count) model(s): $($names -join ', '))"
    } catch {
        Write-Warn 'Ollama not reachable on 11434  ->  run: ollama serve'
    }
}

# ---------------------------------------------------------------------
# Native service control
# ---------------------------------------------------------------------

function Get-PidFile([string]$Service) { return (Join-Path $RunDir "$Service.pid") }

# Returns the pid recorded for a service, but only while that pid is still
# alive. A stale pid file (process died, file left behind) returns $null so
# the next `start` is not silently blocked by a dead entry.
function Get-LiveServicePid([string]$Service) {
    $file = Get-PidFile $Service
    if (-not (Test-Path -LiteralPath $file)) { return $null }

    $raw = (Get-Content -LiteralPath $file | Select-Object -First 1)
    if (-not $raw) { return $null }

    $appPid = 0
    if (-not [int]::TryParse($raw.Trim(), [ref]$appPid)) { return $null }

    if (Get-Process -Id $appPid -ErrorAction SilentlyContinue) { return $appPid }
    return $null
}

function Start-AppService([string]$Service, [string[]]$PyArgs) {
    $py = Assert-Interpreter
    New-Item -ItemType Directory -Force -Path $RunDir, $LogDir | Out-Null

    # Starting a second copy of a service that is already up is what produced
    # the duplicate API/worker/UI processes: the second copy fails to bind the
    # port, dies, and leaves the first one running alongside a stale pid file.
    $live = Get-LiveServicePid $Service
    if ($live) {
        Write-Info "$Service already running (pid $live) - not starting a second copy"
        return
    }

    $out = Join-Path $LogDir "$Service.out.log"
    $err = Join-Path $LogDir "$Service.err.log"

    # Quote any argument containing whitespace so paths with spaces survive.
    $argLine = ($PyArgs | ForEach-Object {
        if ($_ -match '\s') { '"' + $_ + '"' } else { $_ }
    }) -join ' '

    # cmd.exe gives us the stdout/stderr redirection that Win32_Process.Create
    # does not support. cmd strips the outermost pair of quotes, leaving the
    # quoted program path intact.
    $cmdLine = 'cmd.exe /c ""' + $py + '" ' + $argLine +
               ' > "' + $out + '" 2> "' + $err + '""'

    # Win32_Process.Create rather than Start-Process. Start-Process makes the
    # service a child of this shell, so it dies with the terminal that launched
    # it - which is exactly how the API, worker and UI used to disappear and
    # leave Celery jobs queued forever. A process created through WMI is
    # parented to WmiPrvSE instead and survives on its own.
    $result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine      = $cmdLine
        CurrentDirectory = $Root
    }

    if ($result.ReturnValue -ne 0) {
        throw "could not start $Service (Win32_Process.Create returned $($result.ReturnValue))"
    }

    $result.ProcessId | Set-Content -LiteralPath (Get-PidFile $Service)
    Write-Ok "$Service started (pid $($result.ProcessId))  log: logs\$Service.out.log"
}

function Stop-AppService([string]$Service) {
    $file  = Get-PidFile $Service
    $live  = Get-LiveServicePid $Service

    if (-not $live) {
        if (Test-Path -LiteralPath $file) {
            Remove-Item -LiteralPath $file -Force
            Write-Info "$Service had a stale pid file (process already gone) - removed it."
        } else {
            Write-Info "$Service is not running."
        }
        return
    }

    # /T kills the whole tree. Required here: .venv\Scripts\python.exe is a uv
    # trampoline and the launch goes through cmd.exe, so the interpreter that
    # actually serves requests is a CHILD of the pid recorded above (uvicorn
    # reports its own, different pid). Killing the recorded pid alone would
    # leave the server listening.
    # taskkill writes "not found" to stderr, which PowerShell turns into a
    # terminating error while $ErrorActionPreference is 'Stop'; relax it here.
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & taskkill.exe /PID $live /T /F 2>&1 | Out-Null
    $code = $LASTEXITCODE
    $ErrorActionPreference = $previous

    if ($code -eq 0) { Write-Ok "$Service stopped (pid tree from $live)" }
    else             { Write-Info "$Service pid $live was already gone." }

    Remove-Item -LiteralPath $file -Force
}

# ---------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------

function Invoke-Doctor {
    Write-Head 'Interpreter pinning (root cause of 0xc0000005)'
    $where = @(& where.exe python 2>$null)
    if ($where.Count -gt 0) {
        Write-Info "bare 'python' resolves to:"
        $where | ForEach-Object { Write-Info "  $_" }
        if ([string]$where[0] -notlike '*.venv*') {
            Write-Warn "bare 'python' is NOT the project .venv."
            Write-Info "Always start the stack with: .\commands.ps1 start"
        }
    }
    try {
        Write-Info 'all registered interpreters (py -0p):'
        @(& py -0p 2>$null) | ForEach-Object { Write-Info "  $_" }
    } catch {
        Write-Info 'py launcher not available'
    }
    Write-Info "project expects Python $Expected (see .venv\pyvenv.cfg)"

    Write-Head 'Pinned interpreter'
    try {
        $py = Assert-Interpreter
        Write-Ok "$py -> Python $Expected"
    } catch {
        Write-Bad $_.Exception.Message
        return
    }

    # Single quotes only: PowerShell strips embedded double quotes when it
    # hands an argument to a native executable, which corrupts Python source.
    $probe = @(& $py -c @'
import json, pathlib
info = {}
try:
    import torch
    info['version'] = torch.__version__
    info['path'] = str(pathlib.Path(torch.__file__).resolve().parent)
except Exception as exc:
    info['error'] = type(exc).__name__ + ': ' + str(exc)
print(json.dumps(info))
'@)

    if ($LASTEXITCODE -ne 0) {
        Write-Bad "importing torch killed the interpreter (exit $LASTEXITCODE)."
        Write-Info 'That is the 0xc0000005 signature - a native DLL mismatch, not a Python error.'
        Write-Info 'Repair it with:  .\.venv\Scripts\python.exe -m pip install -r requirements.txt'
        return
    }

    try { $info = ($probe -join '') | ConvertFrom-Json } catch { $info = $null }

    if ($info -and $info.version) {
        Write-Ok "torch $($info.version)"
        if ([string]$info.path -like "$Root*") {
            Write-Ok 'torch loaded from inside .venv'
        } else {
            Write-Bad "torch loaded from OUTSIDE .venv: $($info.path)"
            Write-Info 'A second site-packages is shadowing the venv.'
        }
        Write-Info "c10.dll lives in: $(Join-Path $info.path 'lib')"
    } elseif ($info -and $info.error) {
        Write-Bad "torch import failed: $($info.error)"
    } else {
        Write-Warn 'could not parse the torch probe output'
    }

    Write-Head 'Stale bytecode from other interpreters'
    # Excludes .venv, which legitimately holds .pyc files for the pinned
    # interpreter only; we care about bytecode left in the project's own tree.
    $tags = @(
        Get-ChildItem -Path $Root -Recurse -Filter '*.pyc' -ErrorAction SilentlyContinue |
            Where-Object {
                $_.FullName -like '*__pycache__*' -and $_.FullName -notlike '*\.venv\*'
            } |
            ForEach-Object { if ($_.Name -match 'cpython-(\d+)') { "cpython-$($Matches[1])" } } |
            Sort-Object -Unique
    )
    if ($tags.Count -gt 0) {
        Write-Info "pyc tags present: $($tags -join ', ')"
        $foreign = @($tags | Where-Object { $_ -ne 'cpython-311' })
        if ($foreign.Count -gt 0) {
            Write-Warn "bytecode compiled by $($foreign -join ', ') exists - other interpreters have run this project."
            Write-Info 'Cleanup (safe, regenerated automatically):'
            Write-Info '  Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force'
        } else {
            Write-Ok 'only cpython-311 bytecode present'
        }
    }

    Write-Head 'Host data services'
    foreach ($c in @('mm-rag-postgres', 'mmrag-redis')) {
        $state = Get-ContainerState $c
        if ($state -eq 'running') { Write-Ok "$c running" }
        elseif ($state)           { Write-Warn "$c is $state  ->  docker start $c" }
        else                      { Write-Warn "$c not found" }
    }
    if (Test-Port 5433) { Write-Ok 'port 5433 (PostgreSQL) open' } else { Write-Warn 'port 5433 closed' }
    if (Test-Port 6379) { Write-Ok 'port 6379 (Redis) open' }      else { Write-Warn 'port 6379 closed' }

    Write-Head 'Ollama (stays native on Windows)'
    Show-OllamaModels
    $freeGb = Get-FreeRamGb
    if ($freeGb -lt 1.5) {
        Write-Warn "$freeGb GB RAM free - too little for the ~1.3 GB llama3.2:1b buffer"
    } else {
        Write-Ok "$freeGb GB RAM free"
    }

    Write-Head 'Qdrant Cloud'
    $qurl = @(Get-Content -LiteralPath (Join-Path $Root '.env') |
              Where-Object { $_ -match '^QDRANT_URL=' })[0]
    if ($qurl) { Write-Ok "QDRANT_URL configured ($($qurl -replace '^QDRANT_URL=', ''))" }
    else       { Write-Bad 'QDRANT_URL missing from .env' }
}

# ---------------------------------------------------------------------
# start / stop
# ---------------------------------------------------------------------

function Invoke-Start {
    Write-Head 'Pre-flight'
    $py = Assert-Interpreter
    Write-Ok "interpreter pinned to produce Python $Expected"

    foreach ($c in @('mm-rag-postgres', 'mmrag-redis')) {
        if ((Get-ContainerState $c) -ne 'running') {
            Write-Info "starting host container $c"
            & docker start $c | Out-Null
        }
    }
    if (-not (Test-Port 5433)) { throw 'PostgreSQL on 5433 is not reachable.' }
    if (-not (Test-Port 6379)) { throw 'Redis on 6379 is not reachable.' }
    Write-Ok 'PostgreSQL 5433 + Redis 6379 reachable'

    # Not fatal: ingestion and retrieval are fine on a tight machine, only the
    # generation step needs the headroom.
    $freeGb = Get-FreeRamGb
    if ($freeGb -lt 1.5) {
        Write-Warn "$freeGb GB RAM free - a RAG answer needs ~1.3 GB for llama3.2:1b"
        Write-Info 'close other apps if /query returns 500 "failed to allocate buffer"'
    } else {
        Write-Ok "$freeGb GB RAM free"
    }

    Write-Head 'Schema'
    & $py -m backend.init_db

    Write-Head 'Launching'
    Start-AppService 'api' @(
        '-m', 'uvicorn', 'backend.main:app',
        '--host', '127.0.0.1', '--port', '8000'
    )
    Start-AppService 'worker' @(
        '-m', 'celery', '-A', 'backend.worker.celery_app', 'worker',
        '--loglevel=info', '--pool=solo', '--concurrency=1',
        '--without-gossip', '--without-mingle', '--without-heartbeat'
    )
    Start-AppService 'ui' @(
        '-m', 'streamlit', 'run', 'ui/app.py',
        '--server.address', '127.0.0.1', '--server.port', '8502',
        '--server.headless', 'true'
    )

    Write-Head 'Waiting for the API'
    $deadline = (Get-Date).AddSeconds(60)
    while ((Get-Date) -lt $deadline) {
        if (Test-Url "$ApiUrl/health") { Write-Ok "API answering at $ApiUrl"; break }
        Start-Sleep -Seconds 2
    }
    if (-not (Test-Url "$ApiUrl/health")) {
        Write-Bad 'API did not answer within 60s - read logs\api.err.log'
    }

    Write-Host ''
    Write-Host "  UI   : $UiUrl" -ForegroundColor Green
    Write-Host "  API  : $ApiUrl/docs" -ForegroundColor Green
    Write-Host '  stop : .\commands.ps1 stop' -ForegroundColor DarkGray
}

function Invoke-Stop {
    Write-Head 'Stopping'
    foreach ($s in @('ui', 'worker', 'api')) { Stop-AppService $s }
    Write-Info 'Host PostgreSQL / Redis containers were left running (no data touched).'
}

# ---------------------------------------------------------------------
# status
# ---------------------------------------------------------------------

function Invoke-Status {
    Write-Head 'API'
    if (Test-Url "$ApiUrl/health") {
        Write-Ok "GET $ApiUrl/health"
        try {
            $r = Invoke-RestMethod -Uri "$ApiUrl/health/ready" -TimeoutSec 30
            Write-Ok "GET /health/ready -> $($r | ConvertTo-Json -Compress -Depth 4)"
        } catch {
            Write-Warn "GET /health/ready failed: $($_.Exception.Message)"
        }
    } else {
        Write-Bad "API not reachable at $ApiUrl"
    }

    Write-Head 'UI'
    if (Test-Url "$UiUrl/_stcore/health") { Write-Ok "Streamlit up at $UiUrl" }
    else { Write-Bad "Streamlit not reachable at $UiUrl" }

    Write-Head 'Host data services'
    foreach ($c in @('mm-rag-postgres', 'mmrag-redis')) {
        $state = Get-ContainerState $c
        if ($state -eq 'running') { Write-Ok "$c running" } else { Write-Warn "$c -> $state" }
    }

    Write-Head 'Celery queue depth'
    $len = @(& docker exec mmrag-redis redis-cli LLEN celery 2>$null)
    if ($LASTEXITCODE -eq 0 -and $len.Count -gt 0) {
        Write-Info "unacked/queued messages on 'celery': $([string]$len[-1])"
    } else {
        Write-Warn 'could not read queue depth from mmrag-redis'
    }

    Write-Head 'Docker compose (if this mode is used)'
    @(& docker compose ps 2>$null) | ForEach-Object { Write-Info "$_" }
}

# ---------------------------------------------------------------------
# docker
# ---------------------------------------------------------------------

function Invoke-Up {
    & docker compose up -d --build
    if ($LASTEXITCODE -ne 0) { Write-Bad "docker compose up failed (exit $LASTEXITCODE)"; return }
    Write-Host ''
    Write-Host '  UI  : http://localhost:8502' -ForegroundColor Green
    Write-Host '  API : http://localhost:8000/docs' -ForegroundColor Green
    Write-Info 'Logs: .\commands.ps1 logs       Stop: .\commands.ps1 down'
}

function Invoke-Down {
    Write-Info 'Stopping containers. Volumes and data are NOT removed (-v is never passed).'
    & docker compose down
}

# ---------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------

switch ($Action) {
    'doctor'  { Invoke-Doctor }
    'start'   { Invoke-Start }
    'stop'    { Invoke-Stop }
    'status'  { Invoke-Status }
    'init-db' { & (Assert-Interpreter) -m backend.init_db; exit $LASTEXITCODE }
    'up'      { Invoke-Up; exit $LASTEXITCODE }
    'down'    { Invoke-Down; exit $LASTEXITCODE }
    'ps'      { & docker compose ps; exit $LASTEXITCODE }
    'logs'    { & docker compose logs -f --tail=100 }
}

# Native commands run along the way (docker inspect, py -0p, ...) can leave a
# non-zero $LASTEXITCODE behind even when the action succeeded, so the exit
# code is stated explicitly rather than inherited.
exit 0
