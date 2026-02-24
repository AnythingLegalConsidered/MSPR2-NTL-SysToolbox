#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Teardown Lab Proxmox
# ==============================================================================
# Removes all lab VMs and optionally the network bridge.
# USE WITH CAUTION — this destroys VMs and their data.
#
# Usage: bash teardown-lab.sh
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load config
CONFIG_FILE="${1:-}"
if [[ -z "$CONFIG_FILE" ]]; then
    if [[ -f "$SCRIPT_DIR/config.local.env" ]]; then
        CONFIG_FILE="$SCRIPT_DIR/config.local.env"
    else
        CONFIG_FILE="$SCRIPT_DIR/config.env"
    fi
fi
source "$CONFIG_FILE"

echo "=== NTL-SysToolbox — Teardown Lab ==="
echo ""
echo "ATTENTION : Ceci va SUPPRIMER les VMs suivantes :"
echo "  - ${DC01_VMID} (${DC01_NAME})"
echo "  - ${WMSDB_VMID} (${WMSDB_NAME})"
echo "  - ${CLIENT_VMID} (${CLIENT_NAME})"
echo "  - ${SRVOLD_VMID} (${SRVOLD_NAME})"
echo "  - ${SRVLEG_VMID} (${SRVLEG_NAME})"
echo ""
read -rp "Confirmer la suppression ? (oui/non) : " CONFIRM

if [[ "$CONFIRM" != "oui" ]]; then
    echo "Annule."
    exit 0
fi

# Stop and destroy VMs
for VMID in "$DC01_VMID" "$WMSDB_VMID" "$CLIENT_VMID" "$SRVOLD_VMID" "$SRVLEG_VMID"; do
    if qm status "$VMID" &>/dev/null; then
        echo "  Arret VM $VMID..."
        qm stop "$VMID" --timeout 30 2>/dev/null || true
        sleep 2
        echo "  Suppression VM $VMID..."
        qm destroy "$VMID" --purge 2>/dev/null || true
        echo "  [OK] VM $VMID supprimee"
    else
        echo "  [SKIP] VM $VMID n'existe pas"
    fi
done

# Optionally remove bridge
echo ""
read -rp "Supprimer aussi le bridge ${BRIDGE} ? (oui/non) : " REMOVE_BRIDGE

if [[ "$REMOVE_BRIDGE" == "oui" ]]; then
    ifdown "${BRIDGE}" 2>/dev/null || true

    # Remove bridge config from /etc/network/interfaces
    # Create backup first
    cp /etc/network/interfaces /etc/network/interfaces.bak
    sed -i "/# NTL Lab Network/,/MASQUERADE$/d" /etc/network/interfaces
    # Clean up empty lines
    sed -i '/^$/N;/^\n$/d' /etc/network/interfaces

    echo "[OK] Bridge ${BRIDGE} supprime (backup: /etc/network/interfaces.bak)"
else
    echo "[SKIP] Bridge ${BRIDGE} conserve"
fi

echo ""
echo "=== Teardown termine ==="
