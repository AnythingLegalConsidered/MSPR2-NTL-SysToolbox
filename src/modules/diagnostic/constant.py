# --- CONSTANTES DIAGNOSTIC ---------------------------------------------------
# Ports critiques AD : si un de ceux-là est fermé → CRITICAL
# Ports importants : si fermé → WARNING (pas bloquant mais anormal)
# Services Windows à vérifier via WinRM sur le contrôleur de domaine
# Discovery ports : ports scannés pour l'auto-découverte de services sur le réseau
# Service names : mapping port → nom lisible (pour l'affichage des résultats)

CRITICAL_PORTS = [53, 88, 389]
IMPORTANT_PORTS = [445, 3268]

SERVICES = ["NTDS", "DNS", "Netlogon"]

# Discovery — ports scannés pour l'auto-découverte de services
DISCOVERY_PORTS = [22, 80, 443, 3306, 5432, 8006, 8080]

SERVICE_NAMES: dict[int, str] = {
    22: "SSH",
    53: "DNS",
    80: "HTTP",
    88: "Kerberos",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    3268: "LDAP-GC",
    3306: "MySQL",
    5432: "PostgreSQL",
    8006: "Proxmox",
    8080: "HTTP-Proxy",
}
