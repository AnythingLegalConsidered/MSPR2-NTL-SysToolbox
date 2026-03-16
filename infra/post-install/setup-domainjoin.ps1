# ==============================================================================
# NTL-SysToolbox — Generic Domain Join (Windows Clients)
# ==============================================================================
# Joins any Windows machine to the ntl.local domain.
# Used by: PC-SIEGE-02, PC-COMPTA-01, PC-QUAI-WH1/2/3
#
# Prerequisites: DC01 must be up with AD DS configured.
# The script waits for DC01 LDAP before attempting the join.
#
# Run in PowerShell as Administrator:
#   Set-ExecutionPolicy Bypass -Scope Process
#   .\setup-domainjoin.ps1
# ==============================================================================

# --- Configuration ---
$DC01_IP       = "192.168.10.10"
$DOMAIN_NAME   = "ntl.local"
$ADMIN_USER    = "NTL\Administrator"
$ADMIN_PWD     = "NTL@dmin2026!"

Write-Host "=== NTL-SysToolbox - Domain Join ===" -ForegroundColor Cyan
Write-Host "Machine: $env:COMPUTERNAME" -ForegroundColor Cyan

# --- Step 1: Wait for DC01 to be reachable ---
Write-Host "`n[1/3] Attente de DC01 ($DC01_IP)..." -ForegroundColor Yellow

$maxRetries = 60
$retry = 0
while ($retry -lt $maxRetries) {
    if (Test-Connection -ComputerName $DC01_IP -Count 1 -Quiet) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect($DC01_IP, 389)
            $tcp.Close()
            Write-Host "  DC01 est accessible (LDAP OK)" -ForegroundColor Green
            break
        } catch {
            # LDAP not ready yet
        }
    }
    $retry++
    Write-Host "  Tentative $retry/$maxRetries — DC01 pas encore pret..." -ForegroundColor Gray
    Start-Sleep -Seconds 30
}

if ($retry -ge $maxRetries) {
    Write-Host "ERREUR: DC01 injoignable apres $maxRetries tentatives." -ForegroundColor Red
    exit 1
}

# --- Step 2: Set DNS to DC01 ---
Write-Host "`n[2/3] Configuration DNS vers DC01..." -ForegroundColor Yellow

$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses $DC01_IP

Write-Host "  DNS pointe vers $DC01_IP" -ForegroundColor Green

# --- Step 3: Join domain ---
Write-Host "`n[3/3] Jonction au domaine $DOMAIN_NAME..." -ForegroundColor Yellow

# Check if already domain-joined
try {
    $cs = Get-WmiObject Win32_ComputerSystem
    if ($cs.PartOfDomain -and $cs.Domain -eq $DOMAIN_NAME) {
        Write-Host "  Deja membre du domaine $DOMAIN_NAME" -ForegroundColor Green
        exit 0
    }
} catch {}

$credential = New-Object System.Management.Automation.PSCredential($ADMIN_USER,
    (ConvertTo-SecureString $ADMIN_PWD -AsPlainText -Force))

try {
    Add-Computer -DomainName $DOMAIN_NAME -Credential $credential -Force -ErrorAction Stop
    Write-Host "  Jonction au domaine reussie. Redemarrage..." -ForegroundColor Green
    Restart-Computer -Force
} catch {
    Write-Host "  ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
