# ==============================================================================
# NTL-SysToolbox — Post-install DC01 (Windows Server 2022)
# ==============================================================================
# Run this AFTER installing Windows Server 2022 manually.
# Opens PowerShell as Administrator, then:
#   Set-ExecutionPolicy Bypass -Scope Process
#   .\setup-dc01.ps1
#
# This script:
#   1. Configures static IP
#   2. Installs AD DS + DNS roles
#   3. Promotes the server to Domain Controller (ntl.local)
#   4. Creates OUs and test users
#   5. Opens firewall ports
# ==============================================================================

# --- Configuration (modify if needed) ---
$IP_ADDRESS    = "192.168.10.10"
$PREFIX_LENGTH = 24
$GATEWAY       = "192.168.10.1"
$DNS_SERVER    = "127.0.0.1"
$HOSTNAME      = "DC01"
$DOMAIN_NAME   = "ntl.local"
$DOMAIN_NETBIOS = "NTL"
$SAFE_MODE_PWD = "NTL@dmin2026!"

Write-Host "=== NTL-SysToolbox - Setup DC01 ===" -ForegroundColor Cyan

# --- Step 1: Configure static IP ---
Write-Host "`n[1/5] Configuration IP statique..." -ForegroundColor Yellow

$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
if ($null -eq $adapter) {
    Write-Host "ERREUR: Aucune interface reseau active trouvee." -ForegroundColor Red
    exit 1
}

# Remove existing IP config
Remove-NetIPAddress -InterfaceIndex $adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue
Remove-NetRoute -InterfaceIndex $adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue

# Set static IP
New-NetIPAddress -InterfaceIndex $adapter.ifIndex `
    -IPAddress $IP_ADDRESS `
    -PrefixLength $PREFIX_LENGTH `
    -DefaultGateway $GATEWAY

Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses $DNS_SERVER

Write-Host "  IP: $IP_ADDRESS/$PREFIX_LENGTH, GW: $GATEWAY, DNS: $DNS_SERVER" -ForegroundColor Green

# --- Step 2: Rename computer ---
Write-Host "`n[2/5] Renommage en $HOSTNAME..." -ForegroundColor Yellow

$currentName = $env:COMPUTERNAME
if ($currentName -ne $HOSTNAME) {
    Rename-Computer -NewName $HOSTNAME -Force
    Write-Host "  Renomme de $currentName en $HOSTNAME (redemarrage necessaire)" -ForegroundColor Green
} else {
    Write-Host "  Deja nomme $HOSTNAME" -ForegroundColor Green
}

# --- Step 3: Install AD DS + DNS ---
Write-Host "`n[3/5] Installation des roles AD DS + DNS..." -ForegroundColor Yellow

$adFeature = Get-WindowsFeature -Name AD-Domain-Services
if (-not $adFeature.Installed) {
    Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
    Install-WindowsFeature -Name DNS -IncludeManagementTools
    Write-Host "  Roles AD DS + DNS installes" -ForegroundColor Green
} else {
    Write-Host "  Roles deja installes" -ForegroundColor Green
}

# --- Step 4: Promote to Domain Controller ---
Write-Host "`n[4/5] Promotion en Domain Controller ($DOMAIN_NAME)..." -ForegroundColor Yellow
Write-Host "  Le serveur va redemarrer automatiquement apres la promotion." -ForegroundColor Yellow
Write-Host "  Apres le redemarrage, reconnectez-vous et lancez la partie 2 :" -ForegroundColor Yellow
Write-Host "    .\setup-dc01-part2.ps1" -ForegroundColor Yellow

$securePwd = ConvertTo-SecureString $SAFE_MODE_PWD -AsPlainText -Force

# Check if already a DC
try {
    $domain = Get-ADDomain -ErrorAction Stop
    Write-Host "  Deja promu en DC pour $($domain.DNSRoot)" -ForegroundColor Green
    Write-Host "  Passage direct a la creation des OUs/users..." -ForegroundColor Yellow

    # Skip to OU/user creation (Phase 5)
    & "$PSScriptRoot\setup-dc01-part2.ps1"
    exit 0
} catch {
    # Not a DC yet, proceed with promotion
}

Install-ADDSForest `
    -DomainName $DOMAIN_NAME `
    -DomainNetBIOSName $DOMAIN_NETBIOS `
    -InstallDNS:$true `
    -SafeModeAdministratorPassword $securePwd `
    -CreateDnsDelegation:$false `
    -NoRebootOnCompletion:$false `
    -Force:$true

# The server will reboot here.
# After reboot, run setup-dc01-part2.ps1 for OUs and users.
