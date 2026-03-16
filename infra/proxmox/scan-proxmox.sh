#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Scan Proxmox avant deploiement
# ==============================================================================
# Analyse un Proxmox (local ou remote via API) pour verifier que les VMIDs,
# IPs, storage et RAM sont disponibles avant de lancer setup-lab.sh.
#
# Modes:
#   - Auto-detection: si qm est dispo → local, sinon → API
#   - --local  : forcer le mode local (root sur Proxmox)
#   - --remote : forcer le mode API REST
#
# Usage:
#   bash scan-proxmox.sh                  # auto-detect
#   bash scan-proxmox.sh --local          # force local
#   bash scan-proxmox.sh --remote         # force API
#   bash scan-proxmox.sh --help
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Load config ---
CONFIG_FILE=""
MODE=""

for arg in "$@"; do
    case "$arg" in
        --local)  MODE="local" ;;
        --remote) MODE="remote" ;;
        --help|-h) print_usage; exit 0 ;;
        *)
            if [[ -f "$arg" ]]; then
                CONFIG_FILE="$arg"
            fi
            ;;
    esac
done

print_usage() {
    cat <<'USAGE'
Usage: bash scan-proxmox.sh [OPTIONS] [config-file]

Analyse un Proxmox pour verifier la disponibilite des ressources
avant le deploiement du lab NTL (18 VMs).

Options:
  --local     Forcer le mode local (root sur Proxmox host)
  --remote    Forcer le mode API REST Proxmox
  --help, -h  Afficher cette aide

Le mode est auto-detecte: si 'qm' est disponible → local, sinon → API.

En mode remote, configurez dans config.local.env:
  PVE_HOST=https://192.168.1.100:8006
  PVE_NODE=pve
  PVE_TOKEN_ID=user@pam!token-name
  PVE_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
USAGE
}

# Handle --help before sourcing anything
for arg in "$@"; do
    case "$arg" in
        --help|-h) print_usage; exit 0 ;;
    esac
done

if [[ -z "$CONFIG_FILE" ]]; then
    if [[ -f "$SCRIPT_DIR/config.local.env" ]]; then
        CONFIG_FILE="$SCRIPT_DIR/config.local.env"
    else
        CONFIG_FILE="$SCRIPT_DIR/config.env"
    fi
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERREUR: Config introuvable: $CONFIG_FILE"
    exit 1
fi

# shellcheck source=config.env
source "$CONFIG_FILE"
source "$SCRIPT_DIR/lib/common.sh"

VMS_CSV="$SCRIPT_DIR/vms.csv"
IMAGES_CONF="$SCRIPT_DIR/images.conf"

if [[ ! -f "$VMS_CSV" ]]; then
    err "vms.csv introuvable: $VMS_CSV"
    exit 1
fi

# ==============================================================================
# MODE DETECTION
# ==============================================================================
detect_mode() {
    if [[ -n "$MODE" ]]; then
        echo "$MODE"
        return
    fi
    if command -v qm &>/dev/null; then
        echo "local"
    elif [[ -n "${PVE_HOST:-}" && -n "${PVE_TOKEN_ID:-}" ]]; then
        echo "remote"
    else
        err "Impossible de detecter le mode."
        err "  - Mode local: executez sur le Proxmox host (qm requis)"
        err "  - Mode remote: configurez PVE_HOST + PVE_TOKEN_ID + PVE_TOKEN_SECRET"
        exit 1
    fi
}

MODE=$(detect_mode)

# ==============================================================================
# API HELPERS (remote mode)
# ==============================================================================
pve_api() {
    local endpoint="$1"
    if [[ -z "${PVE_HOST:-}" || -z "${PVE_TOKEN_ID:-}" || -z "${PVE_TOKEN_SECRET:-}" ]]; then
        err "Variables PVE_HOST, PVE_TOKEN_ID, PVE_TOKEN_SECRET requises en mode remote."
        exit 1
    fi
    curl -s -k \
        -H "Authorization: PVEAPIToken=${PVE_TOKEN_ID}=${PVE_TOKEN_SECRET}" \
        "${PVE_HOST}${endpoint}" 2>/dev/null
}

pve_node() {
    echo "${PVE_NODE:-pve}"
}

# ==============================================================================
# SCAN: VMIDs
# ==============================================================================
# Globals for results
declare -A USED_VMIDS=()    # vmid → name
VMID_CONFLICTS=0
VMID_FREE=0

scan_vmids_local() {
    # Scan QEMU VMs
    while read -r vmid name status _rest; do
        [[ "$vmid" == "VMID" ]] && continue
        [[ -z "$vmid" ]] && continue
        USED_VMIDS["$vmid"]="$name"
    done < <(qm list 2>/dev/null || true)

    # Scan LXC containers
    while read -r vmid name status _rest; do
        [[ "$vmid" == "VMID" ]] && continue
        [[ -z "$vmid" ]] && continue
        USED_VMIDS["$vmid"]="$name (LXC)"
    done < <(pct list 2>/dev/null || true)
}

scan_vmids_remote() {
    local node
    node=$(pve_node)

    # Scan QEMU VMs
    local qemu_json
    qemu_json=$(pve_api "/api2/json/nodes/${node}/qemu")
    if [[ -n "$qemu_json" ]]; then
        while IFS='|' read -r vmid name; do
            [[ -z "$vmid" ]] && continue
            USED_VMIDS["$vmid"]="$name"
        done < <(echo "$qemu_json" | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', [])
for vm in data:
    print(f\"{vm.get('vmid','')}|{vm.get('name','')}\")
" 2>/dev/null || true)
    fi

    # Scan LXC containers
    local lxc_json
    lxc_json=$(pve_api "/api2/json/nodes/${node}/lxc")
    if [[ -n "$lxc_json" ]]; then
        while IFS='|' read -r vmid name; do
            [[ -z "$vmid" ]] && continue
            USED_VMIDS["$vmid"]="$name (LXC)"
        done < <(echo "$lxc_json" | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', [])
for ct in data:
    print(f\"{ct.get('vmid','')}|{ct.get('name','')}\")
" 2>/dev/null || true)
    fi
}

check_vmids() {
    step "VMIDs ($(wc -l < "$VMS_CSV" | tr -d ' ') lignes dans vms.csv)"

    if [[ "$MODE" == "local" ]]; then
        scan_vmids_local
    else
        scan_vmids_remote
    fi

    log "  ${#USED_VMIDS[@]} VM/CT existantes sur ce Proxmox"
    echo ""

    local line_num=0
    while IFS=',' read -r vmid hostname os_key ip_suffix cores ram_mb disk_gb post_install; do
        line_num=$((line_num + 1))
        [[ $line_num -eq 1 ]] && continue
        [[ -z "$vmid" ]] && continue
        [[ "$vmid" =~ ^# ]] && continue

        if [[ -n "${USED_VMIDS[$vmid]:-}" ]]; then
            printf "  %-6s %-15s ${RED}[CONFLIT]${NC} → VM existante: \"%s\"\n" \
                "$vmid" "$hostname" "${USED_VMIDS[$vmid]}"
            VMID_CONFLICTS=$((VMID_CONFLICTS + 1))
        else
            printf "  %-6s %-15s ${GREEN}[LIBRE]${NC}\n" "$vmid" "$hostname"
            VMID_FREE=$((VMID_FREE + 1))
        fi
    done < "$VMS_CSV"

    echo ""
    local total=$((VMID_FREE + VMID_CONFLICTS))
    if [[ $VMID_CONFLICTS -eq 0 ]]; then
        log "VMIDs: ${VMID_FREE}/${total} libres — aucun conflit"
    else
        err "VMIDs: ${VMID_FREE}/${total} libres, ${VMID_CONFLICTS} conflits"
    fi
}

# ==============================================================================
# SCAN: IPs
# ==============================================================================
declare -A USED_IPS=()    # ip → vmid:name
IP_CONFLICTS=0
IP_FREE=0

scan_ips_local() {
    # Parse /etc/pve/qemu-server/*.conf for IP assignments
    for conf_file in /etc/pve/qemu-server/*.conf; do
        [[ ! -f "$conf_file" ]] && continue
        local vmid
        vmid=$(basename "$conf_file" .conf)
        local name=""
        local ip=""

        # Get VM name
        name=$(grep "^name:" "$conf_file" 2>/dev/null | head -1 | awk '{print $2}')

        # Cloud-init IP (ipconfig0: ip=x.x.x.x/24,gw=...)
        ip=$(grep "^ipconfig" "$conf_file" 2>/dev/null | grep -oP 'ip=\K[0-9.]+' | head -1)

        if [[ -n "$ip" ]]; then
            USED_IPS["$ip"]="${vmid}:${name}"
        fi
    done

    # Also check LXC configs
    for conf_file in /etc/pve/lxc/*.conf; do
        [[ ! -f "$conf_file" ]] && continue
        local vmid
        vmid=$(basename "$conf_file" .conf)
        local name=""
        local ip=""

        name=$(grep "^hostname:" "$conf_file" 2>/dev/null | head -1 | awk '{print $2}')
        ip=$(grep "^net" "$conf_file" 2>/dev/null | grep -oP 'ip=\K[0-9.]+' | head -1)

        if [[ -n "$ip" ]]; then
            USED_IPS["$ip"]="${vmid}:${name} (LXC)"
        fi
    done
}

scan_ips_remote() {
    local node
    node=$(pve_node)

    # Get all QEMU VMs
    local qemu_json
    qemu_json=$(pve_api "/api2/json/nodes/${node}/qemu")
    if [[ -z "$qemu_json" ]]; then return; fi

    local vmids
    vmids=$(echo "$qemu_json" | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', [])
for vm in data:
    print(f\"{vm.get('vmid','')}|{vm.get('name','')}\")
" 2>/dev/null || true)

    while IFS='|' read -r vmid name; do
        [[ -z "$vmid" ]] && continue
        local config_json
        config_json=$(pve_api "/api2/json/nodes/${node}/qemu/${vmid}/config")
        if [[ -n "$config_json" ]]; then
            local ip
            ip=$(echo "$config_json" | python3 -c "
import sys, json, re
data = json.load(sys.stdin).get('data', {})
for key, val in data.items():
    if key.startswith('ipconfig'):
        m = re.search(r'ip=([0-9.]+)', str(val))
        if m:
            print(m.group(1))
            break
" 2>/dev/null || true)
            if [[ -n "$ip" ]]; then
                USED_IPS["$ip"]="${vmid}:${name}"
            fi
        fi
    done <<< "$vmids"
}

check_ips() {
    step "IPs sur ${SUBNET}.0/${CIDR}"

    if [[ "$MODE" == "local" ]]; then
        scan_ips_local
    else
        scan_ips_remote
    fi

    log "  ${#USED_IPS[@]} IPs assignees a des VMs existantes"
    echo ""

    local line_num=0
    while IFS=',' read -r vmid hostname os_key ip_suffix cores ram_mb disk_gb post_install; do
        line_num=$((line_num + 1))
        [[ $line_num -eq 1 ]] && continue
        [[ -z "$vmid" ]] && continue
        [[ "$vmid" =~ ^# ]] && continue

        local target_ip="${SUBNET}.${ip_suffix}"

        if [[ -n "${USED_IPS[$target_ip]:-}" ]]; then
            local owner="${USED_IPS[$target_ip]}"
            printf "  .%-5s %-15s ${RED}[OCCUPEE]${NC} → VM %s\n" \
                "$ip_suffix" "$hostname" "$owner"
            IP_CONFLICTS=$((IP_CONFLICTS + 1))
        else
            printf "  .%-5s %-15s ${GREEN}[LIBRE]${NC}\n" "$ip_suffix" "$hostname"
            IP_FREE=$((IP_FREE + 1))
        fi
    done < "$VMS_CSV"

    echo ""
    local total=$((IP_FREE + IP_CONFLICTS))
    if [[ $IP_CONFLICTS -eq 0 ]]; then
        log "IPs: ${IP_FREE}/${total} libres — aucun conflit"
    else
        err "IPs: ${IP_FREE}/${total} libres, ${IP_CONFLICTS} conflits"
    fi
}

# ==============================================================================
# SCAN: Resources (storage + RAM)
# ==============================================================================
STORAGE_OK=true
RAM_OK=true
REQUIRED_DISK_GB=0
REQUIRED_RAM_MB=0

calc_requirements() {
    local line_num=0
    while IFS=',' read -r vmid hostname os_key ip_suffix cores ram_mb disk_gb post_install; do
        line_num=$((line_num + 1))
        [[ $line_num -eq 1 ]] && continue
        [[ -z "$vmid" ]] && continue
        [[ "$vmid" =~ ^# ]] && continue

        REQUIRED_DISK_GB=$((REQUIRED_DISK_GB + disk_gb))
        REQUIRED_RAM_MB=$((REQUIRED_RAM_MB + ram_mb))
    done < "$VMS_CSV"
}

check_resources_local() {
    step "Ressources"
    calc_requirements

    echo ""

    # Storage
    local storage_line
    storage_line=$(pvesm status 2>/dev/null | grep "^${STORAGE}" | head -1)
    if [[ -n "$storage_line" ]]; then
        local total_bytes avail_bytes
        total_bytes=$(echo "$storage_line" | awk '{print $4}')
        avail_bytes=$(echo "$storage_line" | awk '{print $5}')
        local avail_gb=$((avail_bytes / 1024 / 1024))

        if [[ $avail_gb -ge $REQUIRED_DISK_GB ]]; then
            printf "  Storage: %-12s ${GREEN}%s Go dispo${NC} / %s Go requis  ${GREEN}[OK]${NC}\n" \
                "$STORAGE" "$avail_gb" "$REQUIRED_DISK_GB"
        else
            printf "  Storage: %-12s ${RED}%s Go dispo${NC} / %s Go requis  ${RED}[INSUFFISANT]${NC}\n" \
                "$STORAGE" "$avail_gb" "$REQUIRED_DISK_GB"
            STORAGE_OK=false
        fi
    else
        printf "  Storage: %-12s ${YELLOW}[INTROUVABLE]${NC}\n" "$STORAGE"
        STORAGE_OK=false
    fi

    # RAM
    local total_ram_mb avail_ram_mb
    total_ram_mb=$(free -m | awk '/^Mem:/{print $2}')
    avail_ram_mb=$(free -m | awk '/^Mem:/{print $7}')  # available column

    # In practice, VMs won't all run at once with max RAM — show total system RAM
    if [[ $total_ram_mb -ge $REQUIRED_RAM_MB ]]; then
        printf "  RAM:     %-12s ${GREEN}%s Mo total${NC} / %s Mo requis  ${GREEN}[OK]${NC}\n" \
            "" "$total_ram_mb" "$REQUIRED_RAM_MB"
    else
        printf "  RAM:     %-12s ${YELLOW}%s Mo total${NC} / %s Mo requis  ${YELLOW}[ATTENTION]${NC}\n" \
            "" "$total_ram_mb" "$REQUIRED_RAM_MB"
        warn "  La RAM totale est inferieure a la somme des VMs."
        warn "  En pratique, toutes les VMs ne consomment pas leur max en meme temps."
        RAM_OK=false
    fi
}

check_resources_remote() {
    step "Ressources"
    calc_requirements

    echo ""
    local node
    node=$(pve_node)

    # Node status
    local status_json
    status_json=$(pve_api "/api2/json/nodes/${node}/status")
    if [[ -n "$status_json" ]]; then
        local total_ram_mb
        total_ram_mb=$(echo "$status_json" | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', {}).get('memory', {})
print(int(data.get('total', 0) / 1024 / 1024))
" 2>/dev/null || echo "0")

        if [[ $total_ram_mb -ge $REQUIRED_RAM_MB ]]; then
            printf "  RAM:     ${GREEN}%s Mo total${NC} / %s Mo requis  ${GREEN}[OK]${NC}\n" \
                "$total_ram_mb" "$REQUIRED_RAM_MB"
        else
            printf "  RAM:     ${YELLOW}%s Mo total${NC} / %s Mo requis  ${YELLOW}[ATTENTION]${NC}\n" \
                "$total_ram_mb" "$REQUIRED_RAM_MB"
            RAM_OK=false
        fi
    else
        warn "  Impossible de recuperer les infos du node"
    fi

    # Storage
    local storage_json
    storage_json=$(pve_api "/api2/json/nodes/${node}/storage")
    if [[ -n "$storage_json" ]]; then
        local avail_gb
        avail_gb=$(echo "$storage_json" | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', [])
for s in data:
    if s.get('storage') == '${STORAGE}':
        avail = s.get('avail', 0)
        print(int(avail / 1024 / 1024 / 1024))
        break
else:
    print(0)
" 2>/dev/null || echo "0")

        if [[ $avail_gb -ge $REQUIRED_DISK_GB ]]; then
            printf "  Storage: %-12s ${GREEN}%s Go dispo${NC} / %s Go requis  ${GREEN}[OK]${NC}\n" \
                "$STORAGE" "$avail_gb" "$REQUIRED_DISK_GB"
        else
            printf "  Storage: %-12s ${RED}%s Go dispo${NC} / %s Go requis  ${RED}[INSUFFISANT]${NC}\n" \
                "$STORAGE" "$avail_gb" "$REQUIRED_DISK_GB"
            STORAGE_OK=false
        fi
    else
        warn "  Impossible de recuperer les infos storage"
    fi
}

# ==============================================================================
# VERDICT
# ==============================================================================
print_verdict() {
    step "Verdict"
    echo ""

    local issues=0

    if [[ $VMID_CONFLICTS -gt 0 ]]; then
        err "  ${VMID_CONFLICTS} conflit(s) de VMID"
        issues=$((issues + VMID_CONFLICTS))

        # Suggest offset
        local max_used=0
        for vmid in "${!USED_VMIDS[@]}"; do
            [[ "$vmid" -gt "$max_used" ]] && max_used="$vmid"
        done
        local suggested_base=$(( (max_used / 1000 + 1) * 1000 + 10 ))
        warn "  Suggestion: modifier les VMIDs dans vms.csv (base: ${suggested_base}+)"
    fi

    if [[ $IP_CONFLICTS -gt 0 ]]; then
        err "  ${IP_CONFLICTS} conflit(s) d'IP"
        issues=$((issues + IP_CONFLICTS))
        warn "  Suggestion: modifier le SUBNET dans config.local.env"
    fi

    if [[ "$STORAGE_OK" != "true" ]]; then
        err "  Storage insuffisant"
        issues=$((issues + 1))
        warn "  Suggestion: ajouter du stockage ou reduire les tailles de disque dans vms.csv"
    fi

    if [[ "$RAM_OK" != "true" ]]; then
        warn "  RAM totale inferieure au cumul des VMs (non bloquant)"
    fi

    echo ""
    if [[ $issues -eq 0 ]]; then
        echo -e "  ${GREEN}=== PRET A DEPLOYER ===${NC}"
        echo "  Lancez: bash setup-lab.sh"
    else
        echo -e "  ${RED}=== ${issues} PROBLEME(S) A RESOUDRE ===${NC}"
        echo "  Corrigez les conflits avant de lancer setup-lab.sh"
    fi
    echo ""
}

# ==============================================================================
# MAIN
# ==============================================================================
echo ""
echo "=== NTL Lab — Scan Proxmox ==="
echo "Mode   : $MODE"
echo "Config : $CONFIG_FILE"
echo "VMs    : $VMS_CSV"
echo "Subnet : ${SUBNET}.0/${CIDR}"
echo ""

check_vmids
check_ips

if [[ "$MODE" == "local" ]]; then
    check_resources_local
else
    check_resources_remote
fi

print_verdict
