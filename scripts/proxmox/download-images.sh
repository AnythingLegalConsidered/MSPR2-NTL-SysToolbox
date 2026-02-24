#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Download images for Proxmox lab
# ==============================================================================
# Downloads Ubuntu cloud images and VirtIO drivers.
# Windows ISOs must be downloaded manually (Microsoft requires a form).
#
# Usage: bash download-images.sh
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

echo "=== NTL-SysToolbox — Download Images ==="
echo "Destination: ${ISO_PATH}"
echo ""

# Ensure ISO directory exists
mkdir -p "$ISO_PATH"

# --- Ubuntu 20.04 cloud image ---
if [[ -f "${ISO_PATH}/${CLOUD_IMG_2004}" ]]; then
    echo "[OK] Ubuntu 20.04 cloud image deja presente"
else
    echo "[DL] Telechargement Ubuntu 20.04 cloud image..."
    wget -q --show-progress -O "${ISO_PATH}/${CLOUD_IMG_2004}" \
        "https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img"
    echo "[OK] Ubuntu 20.04 telechargee"
fi

# --- Ubuntu 18.04 cloud image ---
if [[ -f "${ISO_PATH}/${CLOUD_IMG_1804}" ]]; then
    echo "[OK] Ubuntu 18.04 cloud image deja presente"
else
    echo "[DL] Telechargement Ubuntu 18.04 cloud image..."
    wget -q --show-progress -O "${ISO_PATH}/${CLOUD_IMG_1804}" \
        "https://cloud-images.ubuntu.com/bionic/current/bionic-server-cloudimg-amd64.img"
    echo "[OK] Ubuntu 18.04 telechargee"
fi

# --- VirtIO drivers ---
if [[ -f "${ISO_PATH}/${ISO_VIRTIO}" ]]; then
    echo "[OK] VirtIO drivers ISO deja presente"
else
    echo "[DL] Telechargement VirtIO drivers..."
    wget -q --show-progress -O "${ISO_PATH}/${ISO_VIRTIO}" \
        "https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso"
    echo "[OK] VirtIO drivers telechargees"
fi

# --- Windows ISOs (manual download required) ---
echo ""
echo "========================================================================"
echo "  ISOs WINDOWS — Telechargement manuel requis"
echo "========================================================================"
echo ""

check_windows_iso() {
    local VAR_NAME="$1"
    local DESCRIPTION="$2"
    local URL="$3"
    local FILE="${!VAR_NAME:-}"

    if [[ -z "$FILE" ]]; then
        echo "[MANQUE] $DESCRIPTION"
        echo "         Variable $VAR_NAME vide dans config.env"
        echo "         Telecharger depuis : $URL"
        echo "         Puis renseigner le nom du fichier dans config.env"
        echo ""
    elif [[ -f "${ISO_PATH}/${FILE}" ]]; then
        echo "[OK] $DESCRIPTION : $FILE"
    else
        echo "[MANQUE] $DESCRIPTION : $FILE introuvable dans ${ISO_PATH}/"
        echo "         Telecharger depuis : $URL"
        echo ""
    fi
}

check_windows_iso "ISO_WIN2022" \
    "Windows Server 2022 Evaluation" \
    "https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2022"

check_windows_iso "ISO_WIN10" \
    "Windows 10/11" \
    "https://www.microsoft.com/en-us/software-download/windows10ISO"

check_windows_iso "ISO_WIN2012" \
    "Windows Server 2012 R2 Evaluation" \
    "https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2012-r2"

echo "========================================================================"
echo ""
echo "Pour uploader une ISO sur Proxmox depuis votre PC :"
echo "  scp MonISO.iso root@proxmox:${ISO_PATH}/"
echo ""
echo "Ou via la GUI Proxmox : Datacenter > Storage > local > ISO Images > Upload"
echo ""

# --- Summary ---
echo "=== Resume ==="
echo ""
ls -lh "${ISO_PATH}/"*.{img,iso} 2>/dev/null || echo "(aucune image trouvee)"
echo ""
echo "=== Done ==="
