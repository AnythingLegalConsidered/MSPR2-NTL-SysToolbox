# ==============================================================================
# NTL-SysToolbox — Post-install DC02 (Windows Server 2019)
# ==============================================================================
# Promotes DC02 as a secondary Domain Controller in ntl.local.
# Requires DC01 to be fully configured and reachable.
#
# Run in PowerShell as Administrator:
#   Set-ExecutionPolicy Bypass -Scope Process
#   .\dc02-ad-secondary.ps1
# ==============================================================================

# --- Configuration ---
$DC01_IP       = "192.168.10.10"
$DOMAIN_NAME   = "ntl.local"
$DOMAIN_NETBIOS = "NTL"
$SAFE_MODE_PWD = "NTL@dmin2026!"
$ADMIN_USER    = "NTL\Administrator"
$ADMIN_PWD     = "NTL@dmin2026!"

Write-Host "=== NTL-SysToolbox - Setup DC02 (Secondary DC) ===" -ForegroundColor Cyan

# --- Step 1: Wait for DC01 to be reachable ---
Write-Host "`n[1/4] Attente de DC01 ($DC01_IP)..." -ForegroundColor Yellow

$maxRetries = 30
$retry = 0
while ($retry -lt $maxRetries) {
    if (Test-Connection -ComputerName $DC01_IP -Count 1 -Quiet) {
        # Check if LDAP port is open
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
    Write-Host "Verifiez que DC01 est demarre et que AD DS est configure." -ForegroundColor Red
    exit 1
}

# --- Step 2: Set DNS to DC01 ---
Write-Host "`n[2/4] Configuration DNS vers DC01..." -ForegroundColor Yellow

$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses $DC01_IP

Write-Host "  DNS pointe vers $DC01_IP" -ForegroundColor Green

# --- Step 3: Install AD DS role ---
Write-Host "`n[3/4] Installation du role AD DS..." -ForegroundColor Yellow

$adFeature = Get-WindowsFeature -Name AD-Domain-Services
if (-not $adFeature.Installed) {
    Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
    Install-WindowsFeature -Name DNS -IncludeManagementTools
    Write-Host "  Roles AD DS + DNS installes" -ForegroundColor Green
} else {
    Write-Host "  Roles deja installes" -ForegroundColor Green
}

# --- Step 4: Promote as secondary DC ---
Write-Host "`n[4/4] Promotion en DC secondaire pour $DOMAIN_NAME..." -ForegroundColor Yellow
Write-Host "  Le serveur va redemarrer automatiquement." -ForegroundColor Yellow

$securePwd = ConvertTo-SecureString $SAFE_MODE_PWD -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($ADMIN_USER,
    (ConvertTo-SecureString $ADMIN_PWD -AsPlainText -Force))

# Check if already a DC
try {
    $domain = Get-ADDomain -ErrorAction Stop
    Write-Host "  Deja promu en DC pour $($domain.DNSRoot)" -ForegroundColor Green
    exit 0
} catch {
    # Not a DC yet
}

Install-ADDSDomainController `
    -DomainName $DOMAIN_NAME `
    -InstallDns:$true `
    -Credential $credential `
    -SafeModeAdministratorPassword $securePwd `
    -SiteName "Default-First-Site-Name" `
    -ReplicationSourceDC "DC01.$DOMAIN_NAME" `
    -NoRebootOnCompletion:$false `
    -Force:$true

# Server reboots here. After reboot, DC02 replicates AD from DC01.
