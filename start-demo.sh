#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Demo Pre-flight Check (Homelab)
# ==============================================================================
# Run this BEFORE the demo to verify everything is ready.
# Usage: bash start-demo.sh
# ==============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
PASS=0
FAIL=0

check() {
    local desc="$1"
    local cmd="$2"
    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}[OK]${NC} $desc"
        ((PASS++))
    else
        echo -e "  ${RED}[FAIL]${NC} $desc"
        ((FAIL++))
    fi
}

echo "============================================"
echo " NTL-SysToolbox — Demo Pre-flight"
echo "============================================"
echo ""

# --- Network ---
echo -e "${YELLOW}Network${NC}"
check "Route to 172.16.132.0/24" "ping -n 1 -w 2000 172.16.132.10"
check "Ping DC01 (172.16.132.10)" "ping -n 1 -w 2000 172.16.132.10"
check "Ping WMS-DB (172.16.132.20)" "ping -n 1 -w 2000 172.16.132.20"
echo ""

# --- Services ---
echo -e "${YELLOW}Services${NC}"
check "SSH DC01 :22" "ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no -o BatchMode=yes sysadmin@172.16.132.10 'echo ok'"
check "SSH WMS-DB :22" "ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no -o BatchMode=yes sysadmin@172.16.132.20 'echo ok'"
check "LDAP DC01 :389" "ssh -o ConnectTimeout=3 -o BatchMode=yes sysadmin@172.16.132.10 'ss -tlnp | grep -q :389'"
check "DNS DC01 :53" "ssh -o ConnectTimeout=3 -o BatchMode=yes sysadmin@172.16.132.10 'ss -tlnp | grep -q :53'"
check "MySQL WMS-DB :3306" "ssh -o ConnectTimeout=3 -o BatchMode=yes sysadmin@172.16.132.20 'ss -tlnp | grep -q :3306'"
echo ""

# --- Data ---
echo -e "${YELLOW}Data${NC}"
check "AD domain ntl.local" "ssh -o BatchMode=yes sysadmin@172.16.132.10 'samba-tool domain info 127.0.0.1 2>/dev/null | grep -q ntl.local'"
check "AD users exist" "ssh -o BatchMode=yes sysadmin@172.16.132.10 'sudo samba-tool user list --username=Administrator --password=\"NTL@dmin2026!\" 2>/dev/null | grep -q j.dupont'"
check "MySQL wms DB" "ssh -o BatchMode=yes sysadmin@172.16.132.20 'sudo mysql -e \"SELECT 1 FROM wms.shipments LIMIT 1\" 2>/dev/null'"
echo ""

# --- Local toolbox ---
echo -e "${YELLOW}Toolbox${NC}"
check "Python disponible" "python --version"
check "config.yaml existe" "test -f config/config.yaml"
check ".env existe" "test -f .env"
echo ""

# --- Summary ---
echo "============================================"
TOTAL=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
    echo -e " ${GREEN}ALL $TOTAL CHECKS PASSED${NC} — Ready for demo!"
else
    echo -e " ${RED}$FAIL/$TOTAL CHECKS FAILED${NC} — Fix before demo"
fi
echo "============================================"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo "Launch: python src/main.py"
fi
