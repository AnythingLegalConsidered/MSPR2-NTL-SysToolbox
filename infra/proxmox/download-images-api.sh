#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Download cloud images via Proxmox API
# ==============================================================================
# Downloads Linux cloud images directly to Proxmox storage using the API.
# No shell access needed — works from the deployer VM.
#
# Windows ISOs must be uploaded manually via the web UI.
#
# Usage:
#   bash download-images-api.sh
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CONFIG_FILE="${SCRIPT_DIR}/config.local.env"
[[ ! -f "$CONFIG_FILE" ]] && CONFIG_FILE="${SCRIPT_DIR}/config.env"
source "$CONFIG_FILE"
source "$SCRIPT_DIR/lib/common.sh"
source "$SCRIPT_DIR/lib/proxmox-api.sh"

if ! pve_check_config; then exit 1; fi

echo "=== NTL-SysToolbox — Download Images (API mode) ==="
echo ""

# --- Linux cloud images ---
declare -A CLOUD_IMAGES
CLOUD_IMAGES=(
    ["focal-server-cloudimg-amd64.img"]="https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img"
    ["bionic-server-cloudimg-amd64.img"]="https://cloud-images.ubuntu.com/bionic/current/bionic-server-cloudimg-amd64.img"
    ["xenial-server-cloudimg-amd64.img"]="https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img"
    ["debian-11-genericcloud-amd64.qcow2"]="https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.qcow2"
    ["debian-10-genericcloud-amd64.qcow2"]="https://cloud.debian.org/images/cloud/buster/latest/debian-10-genericcloud-amd64.qcow2"
    ["CentOS-7-x86_64-GenericCloud.qcow2"]="https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2"
)

step "Telechargement des cloud images Linux"

for filename in "${!CLOUD_IMAGES[@]}"; do
    url="${CLOUD_IMAGES[$filename]}"

    if api_file_exists "$ISO_STORAGE" "iso" "$filename"; then
        log "  $filename — deja present"
    else
        echo "  Telechargement de $filename..."
        if api_download_url "$ISO_STORAGE" "$url" "$filename" "iso"; then
            log "  $filename — telecharge"
        else
            warn "  $filename — echec (URL: $url)"
        fi
    fi
done

# --- VirtIO drivers ---
step "VirtIO drivers"

VIRTIO_URL="https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso"
if api_file_exists "$ISO_STORAGE" "iso" "virtio-win.iso"; then
    log "  virtio-win.iso — deja present"
else
    echo "  Telechargement de virtio-win.iso..."
    if api_download_url "$ISO_STORAGE" "$VIRTIO_URL" "virtio-win.iso" "iso"; then
        log "  virtio-win.iso — telecharge"
    else
        warn "  virtio-win.iso — echec"
    fi
fi

# --- Summary ---
step "Resume"

echo ""
echo "Images presentes sur ${ISO_STORAGE}:"
api_list_storage "$ISO_STORAGE" "iso" | while read -r volid; do
    echo "  $volid"
done

echo ""
echo "ISOs Windows a uploader manuellement via le web UI:"
echo "  - win2022_eval.iso     (Server 2022 — Microsoft Evaluation Center)"
echo "  - win2019_eval.iso     (Server 2019)"
echo "  - win2016_eval.iso     (Server 2016)"
echo "  - win2012r2_eval.iso   (Server 2012 R2)"
echo "  - win2008r2_eval.iso   (Server 2008 R2)"
echo "  - win11.iso            (Windows 11)"
echo "  - win10.iso            (Windows 10)"
echo "  - win7.iso             (Windows 7)"
echo ""
echo "Upload via: Proxmox Web UI > Datacenter > Storage > ${ISO_STORAGE} > Upload"
