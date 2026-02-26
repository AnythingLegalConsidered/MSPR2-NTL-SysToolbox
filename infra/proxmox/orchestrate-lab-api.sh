#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Lab Orchestrator (API mode)
# ==============================================================================
# Same logic as orchestrate-lab.sh but uses Proxmox API instead of qm.
# Run from the deployer VM or any machine with API access.
#
# Usage:
#   bash orchestrate-lab-api.sh              # default: demo profile
#   bash orchestrate-lab-api.sh essential
#   bash orchestrate-lab-api.sh demo
#   bash orchestrate-lab-api.sh full
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Load config ---
CONFIG_FILE="${SCRIPT_DIR}/config.local.env"
[[ ! -f "$CONFIG_FILE" ]] && CONFIG_FILE="${SCRIPT_DIR}/config.env"
source "$CONFIG_FILE"
source "$SCRIPT_DIR/lib/common.sh"
source "$SCRIPT_DIR/lib/proxmox-api.sh"
source "$SCRIPT_DIR/lib/wait-service.sh"

# --- Parse profile ---
PROFILE="${1:-demo}"
PROFILES_CONF="$SCRIPT_DIR/profiles.conf"
VMS_CSV="$SCRIPT_DIR/vms.csv"
IMAGES_CONF="$SCRIPT_DIR/images.conf"

PROFILE_VMIDS=$(grep "^${PROFILE}|" "$PROFILES_CONF" 2>/dev/null | cut -d'|' -f2)
if [[ -z "$PROFILE_VMIDS" ]]; then
    err "Profil '$PROFILE' inconnu."
    grep -v "^#" "$PROFILES_CONF" | cut -d'|' -f1 | sed 's/^/  - /'
    exit 1
fi

IFS=',' read -ra VMIDS <<< "$PROFILE_VMIDS"

echo ""
echo "=== NTL-SysToolbox — Lab Orchestrator (API mode) ==="
echo "Profil  : $PROFILE (${#VMIDS[@]} VMs)"
echo "API     : $PVE_HOST"
echo ""

# Verify API connectivity
if ! pve_check_config; then exit 1; fi
if ! pve_api GET "/nodes/${PVE_NODE}/status" >/dev/null 2>&1; then
    err "API Proxmox injoignable"
    exit 1
fi

in_profile() {
    local target="$1"
    for vmid in "${VMIDS[@]}"; do
        [[ "$vmid" == "$target" ]] && return 0
    done
    return 1
}

get_hostname() {
    grep "^${1}," "$VMS_CSV" | cut -d',' -f2
}

get_vm_type() {
    local os_key
    os_key=$(grep "^${1}," "$VMS_CSV" | cut -d',' -f3)
    get_image_type "$os_key" "$IMAGES_CONF"
}

# ==============================================================================
# WAVE 0 — PRE-FLIGHT
# ==============================================================================
step "Vague 0 — Pre-flight"

MISSING=0
for vmid in "${VMIDS[@]}"; do
    if ! api_vm_exists "$vmid"; then
        err "VM $vmid ($(get_hostname "$vmid")) n'existe pas"
        MISSING=$((MISSING + 1))
    fi
done

if [[ $MISSING -gt 0 ]]; then
    err "Lancez setup-lab-api.sh d'abord."
    exit 1
fi
log "Toutes les ${#VMIDS[@]} VMs existent"

# Stop all for clean sequencing
echo "Arret des VMs pour sequencement propre..."
for vmid in "${VMIDS[@]}"; do
    status=$(api_vm_status "$vmid" 2>/dev/null)
    if [[ "$status" == "running" ]]; then
        api_stop_vm "$vmid" 30 2>/dev/null || api_force_stop_vm "$vmid" 2>/dev/null || true
    fi
done
sleep 5

# ==============================================================================
# WAVE 1 — LINUX VMs
# ==============================================================================
step "Vague 1 — VMs Linux (cloud-init)"

LINUX_STARTED=0
for vmid in "${VMIDS[@]}"; do
    if [[ "$(get_vm_type "$vmid")" == "linux" ]]; then
        hostname=$(get_hostname "$vmid")
        api_start_vm "$vmid"
        log "$hostname ($vmid) — started"
        LINUX_STARTED=$((LINUX_STARTED + 1))
    fi
done

if [[ $LINUX_STARTED -gt 0 ]]; then
    echo "Attente cloud-init (${LINUX_STARTED} VMs)..."
    sleep 30

    if in_profile "1021"; then
        wait_for_port "${SUBNET}.21" 22 300 "WMS-DB SSH"
        wait_for_port "${SUBNET}.21" 3306 300 "WMS-DB MySQL"
    fi
    if in_profile "1022"; then
        wait_for_port "${SUBNET}.22" 80 300 "WMS-APP HTTP"
    fi
fi
log "Vague 1 terminee"

# ==============================================================================
# WAVE 2 — DOMAIN CONTROLLER
# ==============================================================================
step "Vague 2 — Domain Controller"

if in_profile "1010"; then
    api_start_vm "1010"
    log "DC01 — started"
    echo "Attente AD DS (peut prendre 30-60 min si premiere install)..."
    wait_for_port "${SUBNET}.10" 389 3600 "DC01 LDAP"
    wait_for_port "${SUBNET}.10" 53 60 "DC01 DNS"
    log "DC01 operationnel"
fi

if in_profile "1011"; then
    api_start_vm "1011"
    log "DC02 — started (attend DC01 automatiquement)"
fi

# ==============================================================================
# WAVE 3 — DOMAIN-DEPENDENT SERVERS
# ==============================================================================
step "Vague 3 — Serveurs Windows"

for vmid in 1012 1013 1015; do
    if in_profile "$vmid"; then
        api_start_vm "$vmid"
        log "$(get_hostname "$vmid") ($vmid) — started"
    fi
done

if in_profile "1012"; then
    echo "Attente SRV-FILE (install + domain join)..."
    wait_for_port "${SUBNET}.12" 445 3600 "SRV-FILE SMB" || true
fi

# ==============================================================================
# WAVE 4 — CLIENTS
# ==============================================================================
step "Vague 4 — Clients Windows"

for vmid in 1050 1051 1052 1060 1061 1062; do
    if in_profile "$vmid"; then
        api_start_vm "$vmid"
        log "$(get_hostname "$vmid") ($vmid) — started"
    fi
done

# ==============================================================================
# WAVE 5 — VERIFICATION
# ==============================================================================
step "Vague 5 — Verification"

if [[ -f "${SCRIPT_DIR}/verify-lab.sh" ]]; then
    bash "${SCRIPT_DIR}/verify-lab.sh" "$PROFILE"
else
    echo "verify-lab.sh non trouve. Verification manuelle..."
    for vmid in "${VMIDS[@]}"; do
        hostname=$(get_hostname "$vmid")
        ip_suffix=$(grep "^${vmid}," "$VMS_CSV" | cut -d',' -f4)
        ip="${SUBNET}.${ip_suffix}"
        if ping -c 1 -W 2 "$ip" &>/dev/null; then
            log "  $hostname ($ip) — reachable"
        else
            warn "  $hostname ($ip) — not yet reachable"
        fi
    done
fi

step "Orchestration terminee"
echo ""
echo "Verifier avec: bash verify-lab.sh $PROFILE"
echo "Tester le CLI: python src/main.py"
