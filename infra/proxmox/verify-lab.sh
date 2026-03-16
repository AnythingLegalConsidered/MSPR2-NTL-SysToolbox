#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Lab Verification Dashboard
# ==============================================================================
# Validates that the lab infrastructure is operational.
# Checks: ping, service ports, AD integration, MySQL, and prints a dashboard.
#
# Usage:
#   bash verify-lab.sh              # verify demo profile
#   bash verify-lab.sh essential    # verify essential profile
#   bash verify-lab.sh full         # verify all VMs
#
# Can be run from the Proxmox host or any machine on the lab network.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Load config ---
CONFIG_FILE="${SCRIPT_DIR}/config.local.env"
[[ ! -f "$CONFIG_FILE" ]] && CONFIG_FILE="${SCRIPT_DIR}/config.env"
source "$CONFIG_FILE"

# Colors
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
GRAY='\033[0;90m'
BOLD='\033[1m'
NC='\033[0m'

# --- Parse profile ---
PROFILE="${1:-demo}"
PROFILES_CONF="$SCRIPT_DIR/profiles.conf"
VMS_CSV="$SCRIPT_DIR/vms.csv"
IMAGES_CONF="$SCRIPT_DIR/images.conf"

PROFILE_VMIDS=$(grep "^${PROFILE}|" "$PROFILES_CONF" 2>/dev/null | cut -d'|' -f2)
if [[ -z "$PROFILE_VMIDS" ]]; then
    echo "Profil '$PROFILE' inconnu. Utilisation de 'demo'."
    PROFILE="demo"
    PROFILE_VMIDS=$(grep "^demo|" "$PROFILES_CONF" | cut -d'|' -f2)
fi

IFS=',' read -ra VMIDS <<< "$PROFILE_VMIDS"

# --- Service port map (vmid → service:port pairs) ---
declare -A SERVICE_MAP
SERVICE_MAP=(
    [1010]="LDAP:389 DNS:53 Kerberos:88"
    [1011]="LDAP:389 DNS:53"
    [1012]="SMB:445"
    [1013]=""
    [1015]=""
    [1021]="MySQL:3306 SSH:22"
    [1022]="HTTP:80 SSH:22"
    [1030]=""
    [1040]="NFS:2049 SMB:445"
    [1041]="SSH:22"
    [1042]="SSH:22"
    [1043]="SSH:22"
    [1050]=""
    [1051]=""
    [1052]=""
    [1060]=""
    [1061]=""
    [1062]=""
)

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
WARN_CHECKS=0
FAIL_CHECKS=0

check_port() {
    local ip="$1" port="$2"
    timeout 2 bash -c "echo > /dev/tcp/${ip}/${port}" 2>/dev/null
}

echo ""
echo -e "${BOLD}=== NTL Lab Verification (profil: $PROFILE) ===${NC}"
echo ""

# ==============================================================================
# PHASE 1 — PING
# ==============================================================================
echo -e "${CYAN}--- Phase 1: Connectivite (Ping) ---${NC}"
echo ""

declare -A PING_RESULTS

for vmid in "${VMIDS[@]}"; do
    hostname=$(grep "^${vmid}," "$VMS_CSV" | cut -d',' -f2)
    ip_suffix=$(grep "^${vmid}," "$VMS_CSV" | cut -d',' -f4)
    ip="${SUBNET}.${ip_suffix}"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if ping -c 1 -W 2 "$ip" &>/dev/null; then
        PING_RESULTS[$vmid]="OK"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        PING_RESULTS[$vmid]="DOWN"
        FAIL_CHECKS=$((FAIL_CHECKS + 1))
    fi
done

# ==============================================================================
# PHASE 2 — SERVICE PORTS
# ==============================================================================
echo -e "${CYAN}--- Phase 2: Services ---${NC}"
echo ""

declare -A PORT_RESULTS

for vmid in "${VMIDS[@]}"; do
    ip_suffix=$(grep "^${vmid}," "$VMS_CSV" | cut -d',' -f4)
    ip="${SUBNET}.${ip_suffix}"
    services="${SERVICE_MAP[$vmid]:-}"

    if [[ -z "$services" ]]; then
        PORT_RESULTS[$vmid]="—"
        continue
    fi

    all_ok=true
    port_status=""
    for svc in $services; do
        svc_name=$(echo "$svc" | cut -d':' -f1)
        svc_port=$(echo "$svc" | cut -d':' -f2)

        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        if check_port "$ip" "$svc_port"; then
            port_status="${port_status}${svc_name}:OK "
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            port_status="${port_status}${svc_name}:FAIL "
            all_ok=false
            FAIL_CHECKS=$((FAIL_CHECKS + 1))
        fi
    done

    PORT_RESULTS[$vmid]="$port_status"
done

# ==============================================================================
# PHASE 3 — AD INTEGRATION
# ==============================================================================
echo -e "${CYAN}--- Phase 3: Active Directory ---${NC}"
echo ""

DC01_IP="${SUBNET}.10"
AD_OK=false

# DNS resolution test
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if command -v nslookup &>/dev/null; then
    if nslookup "$AD_DOMAIN" "$DC01_IP" &>/dev/null; then
        echo -e "  DNS resolution ($AD_DOMAIN via DC01): ${GREEN}OK${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        AD_OK=true
    else
        echo -e "  DNS resolution ($AD_DOMAIN via DC01): ${RED}FAIL${NC}"
        FAIL_CHECKS=$((FAIL_CHECKS + 1))
    fi
elif command -v dig &>/dev/null; then
    if dig "@${DC01_IP}" "$AD_DOMAIN" +short &>/dev/null; then
        echo -e "  DNS resolution ($AD_DOMAIN via DC01): ${GREEN}OK${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        AD_OK=true
    else
        echo -e "  DNS resolution ($AD_DOMAIN via DC01): ${RED}FAIL${NC}"
        FAIL_CHECKS=$((FAIL_CHECKS + 1))
    fi
else
    echo -e "  DNS resolution: ${YELLOW}SKIP${NC} (nslookup/dig not available)"
    WARN_CHECKS=$((WARN_CHECKS + 1))
fi

# LDAP bind test
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if command -v ldapsearch &>/dev/null; then
    if ldapsearch -x -H "ldap://${DC01_IP}" -b "dc=ntl,dc=local" -s base "(objectclass=*)" &>/dev/null; then
        echo -e "  LDAP bind (DC01): ${GREEN}OK${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "  LDAP bind (DC01): ${RED}FAIL${NC}"
        FAIL_CHECKS=$((FAIL_CHECKS + 1))
    fi
else
    echo -e "  LDAP bind: ${YELLOW}SKIP${NC} (ldapsearch not available)"
    WARN_CHECKS=$((WARN_CHECKS + 1))
fi

# ==============================================================================
# PHASE 4 — MySQL
# ==============================================================================
echo -e "\n${CYAN}--- Phase 4: MySQL (WMS-DB) ---${NC}"
echo ""

WMSDB_IP="${SUBNET}.21"
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

if command -v mysql &>/dev/null; then
    TABLES=$(mysql -h "$WMSDB_IP" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB" \
        -e "SHOW TABLES;" 2>/dev/null | tail -n +2 | tr '\n' ', ' | sed 's/,$//')
    if [[ -n "$TABLES" ]]; then
        echo -e "  MySQL connection: ${GREEN}OK${NC}"
        echo -e "  Database '$MYSQL_DB' tables: $TABLES"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))

        # Check row counts
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        SHIP_COUNT=$(mysql -h "$WMSDB_IP" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB" \
            -N -e "SELECT COUNT(*) FROM shipments;" 2>/dev/null)
        INV_COUNT=$(mysql -h "$WMSDB_IP" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB" \
            -N -e "SELECT COUNT(*) FROM inventory;" 2>/dev/null)
        echo -e "  Data: shipments=$SHIP_COUNT rows, inventory=$INV_COUNT rows"
        if [[ "$SHIP_COUNT" -gt 0 && "$INV_COUNT" -gt 0 ]]; then
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            WARN_CHECKS=$((WARN_CHECKS + 1))
        fi
    else
        echo -e "  MySQL connection: ${RED}FAIL${NC}"
        FAIL_CHECKS=$((FAIL_CHECKS + 1))
    fi
else
    # Fallback: just check port
    if check_port "$WMSDB_IP" 3306; then
        echo -e "  MySQL port 3306: ${GREEN}OPEN${NC} (mysql client not available for full test)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "  MySQL port 3306: ${RED}CLOSED${NC}"
        FAIL_CHECKS=$((FAIL_CHECKS + 1))
    fi
fi

# ==============================================================================
# PHASE 5 — DASHBOARD
# ==============================================================================
echo ""
echo -e "${BOLD}=== NTL Lab Dashboard ===${NC}"
echo ""

# Header
printf "${BOLD}%-15s %-18s %-8s %-25s %s${NC}\n" "VM" "IP" "Ping" "Services" "Status"
printf "%-15s %-18s %-8s %-25s %s\n" \
    "───────────────" "──────────────────" "────────" "─────────────────────────" "──────"

for vmid in "${VMIDS[@]}"; do
    hostname=$(grep "^${vmid}," "$VMS_CSV" | cut -d',' -f2)
    ip_suffix=$(grep "^${vmid}," "$VMS_CSV" | cut -d',' -f4)
    ip="${SUBNET}.${ip_suffix}"

    # Ping status
    ping_status="${PING_RESULTS[$vmid]}"
    if [[ "$ping_status" == "OK" ]]; then
        ping_display="${GREEN}[OK]${NC}"
    else
        ping_display="${RED}[DOWN]${NC}"
    fi

    # Service status
    svc_display="${PORT_RESULTS[$vmid]:-—}"
    svc_color="$NC"
    if [[ "$svc_display" == *"FAIL"* ]]; then
        svc_color="$RED"
    elif [[ "$svc_display" == "—" ]]; then
        svc_color="$GRAY"
    else
        svc_color="$GREEN"
    fi

    # Overall status
    if [[ "$ping_status" == "DOWN" ]]; then
        overall="${RED}[DOWN]${NC}"
    elif [[ "$svc_display" == *"FAIL"* ]]; then
        overall="${YELLOW}[WARN]${NC}"
    else
        overall="${GREEN}[OK]${NC}"
    fi

    printf "%-15s %-18s %-8b %-25b %b\n" "$hostname" "$ip" "$ping_display" "${svc_color}${svc_display}${NC}" "$overall"
done

# Summary
echo ""
echo "───────────────────────────────────────────────────────────────────────────"
echo ""

TOTAL_VM=${#VMIDS[@]}
PING_OK=0
PING_DOWN=0
for vmid in "${VMIDS[@]}"; do
    if [[ "${PING_RESULTS[$vmid]}" == "OK" ]]; then
        PING_OK=$((PING_OK + 1))
    else
        PING_DOWN=$((PING_DOWN + 1))
    fi
done

echo -e "VMs reachable : ${GREEN}$PING_OK${NC} / $TOTAL_VM"
echo -e "Checks passed : ${GREEN}$PASSED_CHECKS${NC} / $TOTAL_CHECKS"
[[ $WARN_CHECKS -gt 0 ]] && echo -e "Warnings      : ${YELLOW}$WARN_CHECKS${NC}"
[[ $FAIL_CHECKS -gt 0 ]] && echo -e "Failures      : ${RED}$FAIL_CHECKS${NC}"
echo ""

# Overall verdict
if [[ $FAIL_CHECKS -eq 0 && $PING_DOWN -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}Lab status: READY FOR DEMO${NC}"
elif [[ $FAIL_CHECKS -le 2 && $PING_OK -ge 3 ]]; then
    echo -e "${YELLOW}${BOLD}Lab status: PARTIALLY READY (some services still booting)${NC}"
else
    echo -e "${RED}${BOLD}Lab status: NOT READY ($FAIL_CHECKS failures, $PING_DOWN VMs down)${NC}"
fi

echo ""
