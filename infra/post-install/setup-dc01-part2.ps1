# ==============================================================================
# NTL-SysToolbox — Post-install DC01 Part 2 (after reboot)
# ==============================================================================
# Run AFTER the server has rebooted from AD DS promotion.
# This creates OUs, test users, and opens firewall ports.
#
# Usage:
#   Set-ExecutionPolicy Bypass -Scope Process
#   .\setup-dc01-part2.ps1
# ==============================================================================

Write-Host "=== NTL-SysToolbox - Setup DC01 (Part 2) ===" -ForegroundColor Cyan

# --- Step 5: Create OUs and test users ---
Write-Host "`n[5/5] Creation des OUs et utilisateurs de test..." -ForegroundColor Yellow

# Import AD module
Import-Module ActiveDirectory

$baseDN = "DC=ntl,DC=local"

# Create OUs
$ous = @("IT", "Servers", "Logistics")
foreach ($ou in $ous) {
    $ouDN = "OU=$ou,$baseDN"
    if (-not (Get-ADOrganizationalUnit -Filter "Name -eq '$ou'" -ErrorAction SilentlyContinue)) {
        New-ADOrganizationalUnit -Name $ou -Path $baseDN -ProtectedFromAccidentalDeletion $false
        Write-Host "  OU creee: $ouDN" -ForegroundColor Green
    } else {
        Write-Host "  OU existe deja: $ou" -ForegroundColor Gray
    }
}

# Create test users
$users = @(
    @{ Name = "wms-service"; SamAccount = "wms-service"; OU = "OU=IT,$baseDN"; Password = "WmsS3rv!ce"; Description = "WMS Service Account" },
    @{ Name = "admin-ntl"; SamAccount = "admin-ntl"; OU = "OU=IT,$baseDN"; Password = "Adm1n@NTL!"; Description = "NTL Admin Account" },
    @{ Name = "j.dupont"; SamAccount = "j.dupont"; OU = "OU=Logistics,$baseDN"; Password = "L0g1st1cs!"; Description = "Jean Dupont - Logistics" },
    @{ Name = "m.martin"; SamAccount = "m.martin"; OU = "OU=Logistics,$baseDN"; Password = "L0g1st1cs!"; Description = "Marie Martin - Logistics" }
)

foreach ($user in $users) {
    if (-not (Get-ADUser -Filter "SamAccountName -eq '$($user.SamAccount)'" -ErrorAction SilentlyContinue)) {
        $pwd = ConvertTo-SecureString $user.Password -AsPlainText -Force
        New-ADUser `
            -Name $user.Name `
            -SamAccountName $user.SamAccount `
            -UserPrincipalName "$($user.SamAccount)@ntl.local" `
            -Path $user.OU `
            -AccountPassword $pwd `
            -Enabled $true `
            -Description $user.Description `
            -ChangePasswordAtLogon $false `
            -PasswordNeverExpires $true
        Write-Host "  User cree: $($user.SamAccount)" -ForegroundColor Green
    } else {
        Write-Host "  User existe deja: $($user.SamAccount)" -ForegroundColor Gray
    }
}

# Create security group
$groupName = "IT-Admins"
if (-not (Get-ADGroup -Filter "Name -eq '$groupName'" -ErrorAction SilentlyContinue)) {
    New-ADGroup -Name $groupName -GroupScope Global -Path "OU=IT,$baseDN" -Description "IT Administrators"
    Add-ADGroupMember -Identity $groupName -Members "admin-ntl"
    Write-Host "  Groupe cree: $groupName (membre: admin-ntl)" -ForegroundColor Green
}

# --- Firewall rules ---
Write-Host "`nConfiguration firewall..." -ForegroundColor Yellow

$rules = @(
    @{ Name = "NTL-LDAP"; Port = 389; Protocol = "TCP" },
    @{ Name = "NTL-DNS-TCP"; Port = 53; Protocol = "TCP" },
    @{ Name = "NTL-DNS-UDP"; Port = 53; Protocol = "UDP" }
)

foreach ($rule in $rules) {
    $existing = Get-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
    if (-not $existing) {
        New-NetFirewallRule `
            -DisplayName $rule.Name `
            -Direction Inbound `
            -Protocol $rule.Protocol `
            -LocalPort $rule.Port `
            -Action Allow
        Write-Host "  Regle firewall: $($rule.Name) ($($rule.Protocol)/$($rule.Port))" -ForegroundColor Green
    }
}

# --- Verification ---
Write-Host "`n=== Verification ===" -ForegroundColor Cyan

Write-Host "Domaine:" -ForegroundColor Yellow
Get-ADDomain | Select-Object DNSRoot, NetBIOSName, DomainMode | Format-Table

Write-Host "OUs:" -ForegroundColor Yellow
Get-ADOrganizationalUnit -Filter * | Select-Object Name, DistinguishedName | Format-Table

Write-Host "Users:" -ForegroundColor Yellow
Get-ADUser -Filter * -Properties Description | Select-Object SamAccountName, Name, Description, Enabled | Format-Table

Write-Host "DNS:" -ForegroundColor Yellow
Resolve-DnsName -Name "ntl.local" -Server 127.0.0.1 -ErrorAction SilentlyContinue | Format-Table

Write-Host "LDAP (port 389):" -ForegroundColor Yellow
Test-NetConnection -ComputerName 127.0.0.1 -Port 389 | Select-Object TcpTestSucceeded | Format-Table

Write-Host "`n=== DC01 Setup Complete ===" -ForegroundColor Green
Write-Host "  Domaine: ntl.local"
Write-Host "  LDAP: port 389"
Write-Host "  DNS: port 53"
Write-Host "  Users: wms-service, admin-ntl, j.dupont, m.martin"
Write-Host ""
