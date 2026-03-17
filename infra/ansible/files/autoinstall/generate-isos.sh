#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Generate autoinstall ISOs for all VMs
# ==============================================================================
# Prerequisites: genisoimage or mkisofs
# Usage: bash files/autoinstall/generate-isos.sh
# Output ISOs should be uploaded to Proxmox ISOs storage
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}"

# Detect available ISO tool
if command -v genisoimage &>/dev/null; then
    MKISO="genisoimage"
elif command -v mkisofs &>/dev/null; then
    MKISO="mkisofs"
else
    echo "ERROR: Neither genisoimage nor mkisofs found. Install one first."
    exit 1
fi

echo "Using: ${MKISO}"
echo "Output: ${OUTPUT_DIR}"
echo ""

# --- Windows ISOs (floppy-style: autounattend.xml at root) ---

echo "=== Generating autounattend-srvfiles.iso (SRV-FILES) ==="
${MKISO} -o "${OUTPUT_DIR}/autounattend-srvfiles.iso" \
    -J -r -V "OEMDRV" \
    "${SCRIPT_DIR}/winserver-files/"
echo "  -> autounattend-srvfiles.iso OK"

echo "=== Generating autounattend-entrepot01.iso (PC-ENTREPOT-01) ==="
${MKISO} -o "${OUTPUT_DIR}/autounattend-entrepot01.iso" \
    -J -r -V "OEMDRV" \
    "${SCRIPT_DIR}/win10-entrepot/"
echo "  -> autounattend-entrepot01.iso OK"

# --- Ubuntu ISOs (cloud-init: cidata label) ---

echo "=== Generating autoinstall-wmsapp.iso (SRV-WMS-APP) ==="
${MKISO} -o "${OUTPUT_DIR}/autoinstall-wmsapp.iso" \
    -V "cidata" -J -r \
    "${SCRIPT_DIR}/ubuntu-wmsapp/"
echo "  -> autoinstall-wmsapp.iso OK"

echo "=== Generating autoinstall-backup.iso (SRV-BACKUP) ==="
${MKISO} -o "${OUTPUT_DIR}/autoinstall-backup.iso" \
    -V "cidata" -J -r \
    "${SCRIPT_DIR}/ubuntu-backup/"
echo "  -> autoinstall-backup.iso OK"

echo ""
echo "=== All ISOs generated ==="
ls -lh "${OUTPUT_DIR}"/*.iso
echo ""
echo "Upload ISOs to Proxmox storage (ISOs):"
echo "  scp ${OUTPUT_DIR}/autounattend-srvfiles.iso   root@172.16.254.31:/path/to/ISOs/iso/"
echo "  scp ${OUTPUT_DIR}/autounattend-entrepot01.iso  root@172.16.254.31:/path/to/ISOs/iso/"
echo "  scp ${OUTPUT_DIR}/autoinstall-wmsapp.iso       root@172.16.254.31:/path/to/ISOs/iso/"
echo "  scp ${OUTPUT_DIR}/autoinstall-backup.iso       root@172.16.254.31:/path/to/ISOs/iso/"
