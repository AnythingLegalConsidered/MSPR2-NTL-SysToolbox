# ==============================================================================
# NTL-SysToolbox — Post-install CLIENT-01 (Windows 10/11)
# ==============================================================================
# Run after installing Windows 10/11. Installs Python, nmap, Git.
#
# Usage:
#   Set-ExecutionPolicy Bypass -Scope Process
#   .\setup-client01.ps1
# ==============================================================================

# --- Configuration ---
$IP_ADDRESS    = "192.168.10.50"
$PREFIX_LENGTH = 24
$GATEWAY       = "192.168.10.1"
$DNS_SERVER    = "192.168.10.10"  # DC01
$HOSTNAME      = "CLIENT-01"

Write-Host "=== NTL-SysToolbox - Setup CLIENT-01 ===" -ForegroundColor Cyan

# --- Step 1: Configure static IP ---
Write-Host "`n[1/5] Configuration IP statique..." -ForegroundColor Yellow

$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1

Remove-NetIPAddress -InterfaceIndex $adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue
Remove-NetRoute -InterfaceIndex $adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue

New-NetIPAddress -InterfaceIndex $adapter.ifIndex `
    -IPAddress $IP_ADDRESS `
    -PrefixLength $PREFIX_LENGTH `
    -DefaultGateway $GATEWAY

Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses $DNS_SERVER

Write-Host "  IP: $IP_ADDRESS, DNS: $DNS_SERVER" -ForegroundColor Green

# --- Step 2: Rename computer ---
Write-Host "`n[2/5] Renommage en $HOSTNAME..." -ForegroundColor Yellow

if ($env:COMPUTERNAME -ne $HOSTNAME) {
    Rename-Computer -NewName $HOSTNAME -Force
    Write-Host "  Renomme en $HOSTNAME" -ForegroundColor Green
}

# --- Step 3: Install tools via winget ---
Write-Host "`n[3/5] Installation des outils (Python, Git, nmap)..." -ForegroundColor Yellow

# Check if winget is available
$wingetAvailable = Get-Command winget -ErrorAction SilentlyContinue

if ($wingetAvailable) {
    Write-Host "  Installation via winget..."

    # Python 3.12
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent 2>$null
    Write-Host "  Python installe" -ForegroundColor Green

    # Git
    winget install Git.Git --accept-package-agreements --accept-source-agreements --silent 2>$null
    Write-Host "  Git installe" -ForegroundColor Green

    # nmap
    winget install Insecure.Nmap --accept-package-agreements --accept-source-agreements --silent 2>$null
    Write-Host "  nmap installe" -ForegroundColor Green

} else {
    Write-Host "  winget non disponible. Installation manuelle requise :" -ForegroundColor Red
    Write-Host "    - Python : https://www.python.org/downloads/"
    Write-Host "    - Git    : https://git-scm.com/downloads"
    Write-Host "    - nmap   : https://nmap.org/download.html"
    Write-Host ""
    Write-Host "  Ou installez chocolatey puis : choco install python git nmap"
}

# --- Step 4: Refresh PATH ---
Write-Host "`n[4/5] Rafraichissement du PATH..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# --- Step 5: Verify installations ---
Write-Host "`n[5/5] Verification..." -ForegroundColor Yellow

$tools = @("python", "git", "nmap")
foreach ($tool in $tools) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if ($cmd) {
        $version = & $tool --version 2>&1 | Select-Object -First 1
        Write-Host "  $tool : $version" -ForegroundColor Green
    } else {
        Write-Host "  $tool : NON TROUVE (installer manuellement)" -ForegroundColor Red
    }
}

Write-Host "`n=== CLIENT-01 Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines etapes :"
Write-Host "  1. Redemarrer si le hostname a change"
Write-Host "  2. Ouvrir un terminal et cloner le repo :"
Write-Host "     git clone <URL_REPO> NTL-SysToolbox"
Write-Host "     cd NTL-SysToolbox"
Write-Host "     python -m venv venv"
Write-Host "     venv\Scripts\activate"
Write-Host "     pip install -r requirements.txt"
Write-Host "  3. Copier les configs :"
Write-Host "     copy config\config.example.yaml config\config.yaml"
Write-Host "     copy .env.example .env"
Write-Host "  4. Remplir config.yaml et .env avec les vraies valeurs"
Write-Host ""
