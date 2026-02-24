#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Download images for Proxmox lab
# ==============================================================================
# Downloads Linux cloud images and VirtIO drivers automatically.
# Windows ISOs must be downloaded manually (Microsoft Eval Center).
#
# Reads images.conf to know which Linux cloud images are needed.
#
# Usage: bash download-images.sh [config.env]
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

IMAGES_CONF="$SCRIPT_DIR/images.conf"

echo "=== NTL-SysToolbox — Download Images ==="
echo "Destination: ${ISO_PATH}"
echo ""

mkdir -p "$ISO_PATH"

# ==============================================================================
# LINUX CLOUD IMAGES (auto-download)
# ==============================================================================
step "Cloud images Linux"

# URL mapping for cloud images
declare -A CLOUD_URLS=(
    ["focal-server-cloudimg-amd64.img"]="https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img"
    ["bionic-server-cloudimg-amd64.img"]="https://cloud-images.ubuntu.com/bionic/current/bionic-server-cloudimg-amd64.img"
    ["xenial-server-cloudimg-amd64.img"]="https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img"
    ["debian-11-genericcloud-amd64.qcow2"]="https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.qcow2"
    ["debian-10-genericcloud-amd64.qcow2"]="https://cloud.debian.org/images/cloud/buster/latest/debian-10-genericcloud-amd64.qcow2"
    ["CentOS-7-x86_64-GenericCloud.qcow2"]="https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2"
)

# Collect unique Linux image files from images.conf
LINUX_IMAGES=()
while IFS='|' read -r os_key vm_type image_file template ostype; do
    [[ "$os_key" =~ ^# ]] && continue
    [[ -z "$os_key" ]] && continue
    [[ "$vm_type" != "linux" ]] && continue

    # Deduplicate
    already=false
    for existing in "${LINUX_IMAGES[@]:-}"; do
        [[ "$existing" == "$image_file" ]] && already=true
    done
    $already && continue

    LINUX_IMAGES+=("$image_file")
done < "$IMAGES_CONF"

for img in "${LINUX_IMAGES[@]}"; do
    if [[ -f "${ISO_PATH}/${img}" ]]; then
        log "$img deja presente"
    elif [[ -n "${CLOUD_URLS[$img]:-}" ]]; then
        echo "[DL] Telechargement $img..."
        wget -q --show-progress -O "${ISO_PATH}/${img}" "${CLOUD_URLS[$img]}"
        log "$img telechargee"
    else
        warn "$img — URL inconnue, telechargement manuel requis"
    fi
done

# ==============================================================================
# VIRTIO DRIVERS (auto-download)
# ==============================================================================
step "VirtIO drivers"

VIRTIO_URL="https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso"

if [[ -f "${ISO_PATH}/virtio-win.iso" ]]; then
    log "virtio-win.iso deja presente"
else
    echo "[DL] Telechargement VirtIO drivers..."
    wget -q --show-progress -O "${ISO_PATH}/virtio-win.iso" "$VIRTIO_URL"
    log "virtio-win.iso telechargee"
fi

# ==============================================================================
# WINDOWS ISOs (manual download — display checklist)
# ==============================================================================
step "ISOs Windows (telechargement manuel)"

echo ""

# Collect unique Windows ISOs from images.conf
declare -A WIN_URLS=(
    ["win2022_eval.iso"]="https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2022"
    ["win2019_eval.iso"]="https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2019"
    ["win2016_eval.iso"]="https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2016"
    ["win2012r2_eval.iso"]="https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2012-r2"
    ["win2008r2_eval.iso"]="https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2008-r2"
    ["win11.iso"]="https://www.microsoft.com/en-us/software-download/windows11"
    ["win10.iso"]="https://www.microsoft.com/en-us/software-download/windows10ISO"
    ["win7.iso"]="https://archive.org (or your own source)"
)

while IFS='|' read -r os_key vm_type image_file template ostype; do
    [[ "$os_key" =~ ^# ]] && continue
    [[ -z "$os_key" ]] && continue
    [[ "$vm_type" != "windows" ]] && continue

    if [[ -f "${ISO_PATH}/${image_file}" ]]; then
        log "$image_file ($os_key) — presente"
    else
        warn "$image_file ($os_key) — MANQUANTE"
        echo "     Telecharger: ${WIN_URLS[$image_file]:-URL inconnue}"
        echo ""
    fi
done < "$IMAGES_CONF"

echo ""
echo "Pour uploader une ISO sur Proxmox :"
echo "  scp MonISO.iso root@proxmox:${ISO_PATH}/"
echo "  ou via GUI: Datacenter > Storage > local > ISO Images > Upload"

# ==============================================================================
# SUMMARY
# ==============================================================================
step "Resume"

echo ""
echo "Fichiers dans ${ISO_PATH}/ :"
ls -lh "${ISO_PATH}/"*.{img,iso,qcow2} 2>/dev/null || echo "  (aucune image trouvee)"
echo ""
echo "=== Done ==="
