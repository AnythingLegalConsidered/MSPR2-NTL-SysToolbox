#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Generate autounattend.xml from template
# ==============================================================================
# Replaces placeholders in template XML with VM-specific values.
# Creates a directory with autounattend.xml ready to be packed into ISO.
#
# Usage: gen-autounattend.sh <template> <output_dir> <hostname> <ip> <network> <mask> <gateway> <dns> <admin_pwd> <os_key> [post_install]
# ==============================================================================

set -euo pipefail

TEMPLATE="$1"
OUTPUT_DIR="$2"
HOSTNAME="$3"
IP_ADDRESS="$4"
NETWORK="$5"
SUBNET_MASK="$6"
GATEWAY="$7"
DNS_SERVER="$8"
ADMIN_PASSWORD="$9"
OS_KEY="${10}"
POST_INSTALL="${11:-}"

mkdir -p "$OUTPUT_DIR"

# --- Determine product key and image name based on OS ---
PRODUCT_KEY=""
IMAGE_NAME=""
IMAGE_INDEX="1"

case "$OS_KEY" in
    win-server-2022)
        PRODUCT_KEY="VDYBN-27WPP-V4HQT-9VMD4-VMK7H"
        IMAGE_NAME="Windows Server 2022 SERVERSTANDARD"
        IMAGE_INDEX="2"
        ;;
    win-server-2019)
        PRODUCT_KEY="N69G4-B89J2-4G8F4-WWYCC-J464C"
        IMAGE_NAME="Windows Server 2019 SERVERSTANDARD"
        IMAGE_INDEX="2"
        ;;
    win-server-2016)
        PRODUCT_KEY="WC2BQ-8NRM3-FDDYY-2BFGV-KHKQY"
        IMAGE_NAME="Windows Server 2016 SERVERSTANDARD"
        IMAGE_INDEX="2"
        ;;
    win-server-2012r2)
        PRODUCT_KEY="D2N9P-3P6X9-2R39C-7RTCD-MDVJX"
        IMAGE_NAME="Windows Server 2012 R2 SERVERSTANDARD"
        IMAGE_INDEX="2"
        ;;
    win-server-2008r2)
        PRODUCT_KEY="YC6KT-GKW9T-YTKYR-T4X34-R7VHC"
        IMAGE_NAME="Windows Server 2008 R2 SERVERSTANDARD"
        IMAGE_INDEX="1"
        ;;
    win-11)
        PRODUCT_KEY=""
        IMAGE_NAME="Windows 11 Pro"
        IMAGE_INDEX="1"
        ;;
    win-10)
        PRODUCT_KEY=""
        IMAGE_NAME="Windows 10 Pro"
        IMAGE_INDEX="1"
        ;;
    win-7)
        PRODUCT_KEY=""
        IMAGE_NAME="Windows 7 PROFESSIONAL"
        IMAGE_INDEX="1"
        ;;
esac

# --- Build post-install command block ---
POST_INSTALL_CMD=""
if [[ -n "$POST_INSTALL" ]]; then
    # The post-install script will be on the autounattend ISO (D:\ or E:\)
    POST_INSTALL_CMD="powershell.exe -ExecutionPolicy Bypass -File D:\\${POST_INSTALL}"
fi

# --- Generate autounattend.xml ---
sed \
    -e "s|{{HOSTNAME}}|${HOSTNAME}|g" \
    -e "s|{{IP_ADDRESS}}|${IP_ADDRESS}|g" \
    -e "s|{{SUBNET_MASK}}|${SUBNET_MASK}|g" \
    -e "s|{{GATEWAY}}|${GATEWAY}|g" \
    -e "s|{{DNS_SERVER}}|${DNS_SERVER}|g" \
    -e "s|{{ADMIN_PASSWORD}}|${ADMIN_PASSWORD}|g" \
    -e "s|{{PRODUCT_KEY}}|${PRODUCT_KEY}|g" \
    -e "s|{{IMAGE_NAME}}|${IMAGE_NAME}|g" \
    -e "s|{{IMAGE_INDEX}}|${IMAGE_INDEX}|g" \
    -e "s|{{POST_INSTALL_CMD}}|${POST_INSTALL_CMD}|g" \
    "$TEMPLATE" > "${OUTPUT_DIR}/autounattend.xml"

# --- Copy post-install script if specified ---
SCRIPT_BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -n "$POST_INSTALL" && -f "${SCRIPT_BASE_DIR}/post-install/${POST_INSTALL}" ]]; then
    cp "${SCRIPT_BASE_DIR}/post-install/${POST_INSTALL}" "${OUTPUT_DIR}/${POST_INSTALL}"

    # Also copy part2 script if it exists (for DC01)
    local_base="${POST_INSTALL%.ps1}"
    if [[ -f "${SCRIPT_BASE_DIR}/post-install/${local_base}-part2.ps1" ]]; then
        cp "${SCRIPT_BASE_DIR}/post-install/${local_base}-part2.ps1" "${OUTPUT_DIR}/"
    fi
fi

echo "  Generated: ${OUTPUT_DIR}/autounattend.xml (${OS_KEY})"
