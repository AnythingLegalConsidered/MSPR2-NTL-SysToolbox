#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Teardown Lab Proxmox
# ==============================================================================
# Reads vms.csv and destroys all lab VMs. Optionally removes the bridge.
# USE WITH CAUTION — this destroys VMs and their data.
#
# Usage: bash teardown-lab.sh [config.env]
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Load config ---
CONFIG_FILE="${1:-}"
if [[ -z "$CONFIG_FILE" ]]; then
    if [[ -f "$SCRIPT_DIR/config.local.env" ]]; then
        CONFIG_FILE="$SCRIPT_DIR/config.local.env"
    else
        CONFIG_FILE="$SCRIPT_DIR/config.env"
    fi
fi
source "$CONFIG_FILE"
source "$SCRIPT_DIR/lib/common.sh"

VMS_CSV="$SCRIPT_DIR/vms.csv"
IMAGES_CONF="$SCRIPT_DIR/images.conf"

echo "=== NTL-SysToolbox — Teardown Lab ==="
echo ""
echo "ATTENTION : Ceci va SUPPRIMER les VMs suivantes :"
echo ""

# List all VMs
list_vm() {
    local vmid="$1" hostname="$2" os_key="$3" ip_suffix="$4"
    shift 4; shift 3; shift
    printf "  %-7s %-15s %-22s %s\n" "$vmid" "$hostname" "$os_key" "${SUBNET}.${ip_suffix}"
}

printf "  %-7s %-15s %-22s %s\n" "VMID" "Hostname" "OS" "IP"
printf "  %-7s %-15s %-22s %s\n" "-----" "--------" "--" "--"
parse_vms "$VMS_CSV" list_vm

echo ""
read -rp "Confirmer la suppression de TOUTES ces VMs ? (oui/non) : " CONFIRM

if [[ "$CONFIRM" != "oui" ]]; then
    echo "Annule."
    exit 0
fi

echo ""

# Stop and destroy each VM
destroy_vm() {
    local vmid="$1" hostname="$2"
    shift 7

    if vm_exists "$vmid"; then
        echo "  Arret VM $vmid ($hostname)..."
        qm stop "$vmid" --timeout 30 2>/dev/null || true
        sleep 2
        echo "  Suppression VM $vmid ($hostname)..."
        qm destroy "$vmid" --purge 2>/dev/null || true
        log "VM $vmid ($hostname) supprimee"
    else
        echo "  [SKIP] VM $vmid ($hostname) n'existe pas"
    fi
}

parse_vms "$VMS_CSV" destroy_vm

# Clean up generated autounattend ISOs
echo ""
echo "Nettoyage ISOs autounattend..."
rm -f "${ISO_PATH}"/autounattend-*.iso 2>/dev/null && log "ISOs autounattend supprimees" || true

# Clean up work directory
if [[ -d "${WORK_DIR:-/tmp/ntl-lab}" ]]; then
    rm -rf "${WORK_DIR:-/tmp/ntl-lab}"
    log "Dossier temporaire nettoye"
fi

# Optionally remove bridge
echo ""
read -rp "Supprimer aussi le bridge ${BRIDGE} ? (oui/non) : " REMOVE_BRIDGE

if [[ "$REMOVE_BRIDGE" == "oui" ]]; then
    ifdown "${BRIDGE}" 2>/dev/null || true
    cp /etc/network/interfaces /etc/network/interfaces.bak
    sed -i "/# NTL Lab Network/,/MASQUERADE$/d" /etc/network/interfaces
    sed -i '/^$/N;/^\n$/d' /etc/network/interfaces
    log "Bridge ${BRIDGE} supprime (backup: /etc/network/interfaces.bak)"
else
    echo "[SKIP] Bridge ${BRIDGE} conserve"
fi

echo ""
echo "=== Teardown termine ==="
