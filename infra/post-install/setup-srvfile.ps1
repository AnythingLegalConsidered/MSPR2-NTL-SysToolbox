# ==============================================================================
# NTL-SysToolbox — Post-install SRV-FILE (Windows Server 2012 R2)
# ==============================================================================
# Joins domain and creates SMB shares for NordTransit Logistics.
# Requires DC01 to be fully configured and reachable.
#
# Run in PowerShell as Administrator:
#   Set-ExecutionPolicy Bypass -Scope Process
#   .\setup-srvfile.ps1
# ==============================================================================

# --- Configuration ---
$DC01_IP       = "192.168.10.10"
$DOMAIN_NAME   = "ntl.local"
$ADMIN_USER    = "NTL\Administrator"
$ADMIN_PWD     = "NTL@dmin2026!"

Write-Host "=== NTL-SysToolbox - Setup SRV-FILE ===" -ForegroundColor Cyan

# --- Step 1: Wait for DC01 to be reachable ---
Write-Host "`n[1/5] Attente de DC01 ($DC01_IP)..." -ForegroundColor Yellow

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
        } catch {}
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
Write-Host "`n[2/5] Configuration DNS vers DC01..." -ForegroundColor Yellow

$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses $DC01_IP

Write-Host "  DNS pointe vers $DC01_IP" -ForegroundColor Green

# --- Step 3: Join domain ---
Write-Host "`n[3/5] Jonction au domaine $DOMAIN_NAME..." -ForegroundColor Yellow

$credential = New-Object System.Management.Automation.PSCredential($ADMIN_USER,
    (ConvertTo-SecureString $ADMIN_PWD -AsPlainText -Force))

try {
    $cs = Get-WmiObject Win32_ComputerSystem
    if ($cs.PartOfDomain -and $cs.Domain -eq $DOMAIN_NAME) {
        Write-Host "  Deja membre du domaine $DOMAIN_NAME" -ForegroundColor Green
    } else {
        Add-Computer -DomainName $DOMAIN_NAME -Credential $credential -Force -ErrorAction Stop
        Write-Host "  Jonction au domaine reussie" -ForegroundColor Green
    }
} catch {
    Write-Host "  WARN: Domain join failed ($($_.Exception.Message)). Continuing..." -ForegroundColor Yellow
}

# --- Step 4: Create SMB Shares ---
Write-Host "`n[4/5] Creation des partages SMB..." -ForegroundColor Yellow

# Create share directories
$shares = @(
    @{ Name = "Logistics"; Path = "C:\Shares\Logistics"; Desc = "Documents logistique NTL" },
    @{ Name = "Compta";    Path = "C:\Shares\Compta";    Desc = "Documents comptabilite NTL" },
    @{ Name = "IT";        Path = "C:\Shares\IT";        Desc = "Outils et scripts IT" }
)

foreach ($share in $shares) {
    New-Item -Path $share.Path -ItemType Directory -Force | Out-Null

    # Use net share for 2012 R2 compatibility (New-SmbShare may not be available)
    $existing = net share 2>$null | Select-String "^$($share.Name)\s"
    if ($existing) {
        Write-Host "  Share '$($share.Name)' existe deja" -ForegroundColor Green
    } else {
        net share "$($share.Name)=$($share.Path)" "/GRANT:Everyone,FULL" "/REMARK:$($share.Desc)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Share '$($share.Name)' cree ($($share.Path))" -ForegroundColor Green
        } else {
            # Fallback: try New-SmbShare (Server 2012 R2 with PS 4.0+)
            try {
                New-SmbShare -Name $share.Name -Path $share.Path -FullAccess "Everyone" -Description $share.Desc -ErrorAction Stop
                Write-Host "  Share '$($share.Name)' cree via PowerShell ($($share.Path))" -ForegroundColor Green
            } catch {
                Write-Host "  WARN: Cannot create share '$($share.Name)': $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    }
}

# --- Step 5: Firewall ---
Write-Host "`n[5/5] Configuration firewall..." -ForegroundColor Yellow

try {
    # Enable File and Printer Sharing rules
    Get-NetFirewallRule -DisplayGroup "File And Printer Sharing" -ErrorAction SilentlyContinue |
        Enable-NetFirewallRule -ErrorAction SilentlyContinue
    Write-Host "  Regles 'File And Printer Sharing' activees" -ForegroundColor Green
} catch {
    # Fallback for older Windows
    netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=Yes 2>$null
    Write-Host "  Firewall configure via netsh" -ForegroundColor Green
}

Write-Host "`n=== SRV-FILE Setup termine ===" -ForegroundColor Cyan
Write-Host "Shares disponibles:" -ForegroundColor Cyan
net share | Select-String -Pattern "Logistics|Compta|IT"

# Reboot for domain join to take effect
Write-Host "`nRedemarrage dans 10 secondes (domain join)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Restart-Computer -Force
