#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Setup Lab via Proxmox API (no shell access needed)
# ==============================================================================
# Creates all 18 VMs using the Proxmox REST API instead of `qm` commands.
# Run this from the deployer VM or any machine with curl + python3.
#
# Usage:
#   bash setup-lab-api.sh                # uses config.local.env
#   bash setup-lab-api.sh my-config.env
#
# Prerequisites:
#   - API token created in Proxmox web UI (Datacenter > Permissions > API Tokens)
#   - PVE_HOST, PVE_NODE, PVE_TOKEN_ID, PVE_TOKEN_SECRET set in config.local.env
#   - ISOs uploaded to Proxmox storage (via web UI or download-images-api.sh)
#   - curl, python3, genisoimage installed
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

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERREUR: Config introuvable: $CONFIG_FILE"
    exit 1
fi

source "$CONFIG_FILE"
source "$SCRIPT_DIR/lib/common.sh"
source "$SCRIPT_DIR/lib/proxmox-api.sh"

VMS_CSV="$SCRIPT_DIR/vms.csv"
IMAGES_CONF="$SCRIPT_DIR/images.conf"
WORK_DIR="${WORK_DIR:-/tmp/ntl-lab}"

# ==============================================================================
# PRE-FLIGHT CHECKS
# ==============================================================================
step "Pre-flight checks (API mode)"

# Check required tools
for cmd in curl python3; do
    if ! command -v "$cmd" &>/dev/null; then
        err "$cmd requis. Installez-le: apt install $cmd"
        exit 1
    fi
done

# Check API config
if ! pve_check_config; then
    exit 1
fi

# Test API connectivity
echo "Test de connexion API vers $PVE_HOST..."
if ! pve_api GET "/nodes/${PVE_NODE}/status" >/dev/null 2>&1; then
    err "Impossible de se connecter a l'API Proxmox."
    err "Verifiez PVE_HOST ($PVE_HOST) et les tokens."
    exit 1
fi
log "API Proxmox accessible"

# Check for VMID conflicts
CONFLICTS=0
check_vmid_conflict_api() {
    local vmid="$1" hostname="$2"
    shift 7
    if api_vm_exists "$vmid"; then
        err "VM ID $vmid ($hostname) deja utilisee !"
        CONFLICTS=$((CONFLICTS + 1))
    fi
}
parse_vms "$VMS_CSV" check_vmid_conflict_api
if [[ $CONFLICTS -gt 0 ]]; then
    err "$CONFLICTS conflits de VM IDs."
    exit 1
fi
log "Aucun conflit de VM IDs"

# Count VMs
TOTAL_LINUX=0
TOTAL_WINDOWS=0
count_vms() {
    local os_key="$3"
    local vm_type
    vm_type=$(get_image_type "$os_key" "$IMAGES_CONF")
    if [[ "$vm_type" == "linux" ]]; then
        TOTAL_LINUX=$((TOTAL_LINUX + 1))
    else
        TOTAL_WINDOWS=$((TOTAL_WINDOWS + 1))
    fi
}
parse_vms "$VMS_CSV" count_vms

echo ""
echo "=== NTL-SysToolbox — Setup Lab API (${TOTAL_LINUX} Linux + ${TOTAL_WINDOWS} Windows) ==="
echo "API    : $PVE_HOST (node: $PVE_NODE)"
echo "Reseau : ${SUBNET}.0/${CIDR} sur ${BRIDGE}"
echo ""

# Derive DNS
DNS_SERVER=$(get_dns_server "$VMS_CSV" "$SUBNET")

# ==============================================================================
# PHASE 1 — NETWORK (check bridge)
# ==============================================================================
step "Phase 1 — Verification reseau (bridge $BRIDGE)"

if api_bridge_exists "$BRIDGE"; then
    log "Bridge $BRIDGE existe"
else
    warn "Bridge $BRIDGE n'existe pas."
    echo "  Tentative de creation via API..."
    if api_create_bridge "$BRIDGE" "$GATEWAY" "$CIDR" 2>/dev/null; then
        log "Bridge $BRIDGE cree"
    else
        err "Impossible de creer le bridge $BRIDGE."
        err "Demandez a l'admin de creer le bridge, ou utilisez un bridge existant."
        echo ""
        echo "Bridges disponibles:"
        api_list_networks | grep bridge
        exit 1
    fi
fi

# ==============================================================================
# PHASE 2 — CHECK IMAGES
# ==============================================================================
step "Phase 2 — Verification des images"

check_image() {
    local vmid="$1" hostname="$2" os_key="$3"
    shift 7
    local img_file
    img_file=$(get_image_file "$os_key" "$IMAGES_CONF")
    local vm_type
    vm_type=$(get_image_type "$os_key" "$IMAGES_CONF")

    if api_file_exists "$ISO_STORAGE" "iso" "$img_file"; then
        log "  $img_file — present"
    else
        warn "  $img_file — MANQUANT ($hostname)"
        if [[ "$vm_type" == "linux" ]]; then
            echo "    -> Lancez: bash download-images-api.sh"
        else
            echo "    -> Uploadez via le web UI : Datacenter > Storage > ${ISO_STORAGE} > Upload"
        fi
    fi
}
parse_vms "$VMS_CSV" check_image

# Check VirtIO
if ! api_file_exists "$ISO_STORAGE" "iso" "virtio-win.iso"; then
    warn "virtio-win.iso manquant — les VMs Windows ne detecteront pas les disques."
fi

# ==============================================================================
# PHASE 3 — CREATE VMs
# ==============================================================================
step "Phase 3 — Creation des VMs"

mkdir -p "$WORK_DIR"

CREATED_LINUX=0
CREATED_WINDOWS=0
FAILED=0

create_linux_vm_api() {
    local VMID="$1" HOSTNAME="$2" OS_KEY="$3" IP_SUFFIX="$4"
    local CORES="$5" RAM="$6" DISK="$7" POST_INSTALL="$8"

    local IP="${SUBNET}.${IP_SUFFIX}"
    local IMG_FILE OSTYPE
    IMG_FILE=$(get_image_file "$OS_KEY" "$IMAGES_CONF")
    OSTYPE=$(get_image_ostype "$OS_KEY" "$IMAGES_CONF")

    echo ""
    echo "  Creating Linux VM ${VMID} (${HOSTNAME}) — ${OS_KEY}..."

    # Create VM with cloud image import
    # The import-from syntax works on Proxmox 8.0+
    if ! api_create_vm "$VMID" \
        "name=${HOSTNAME}" \
        "cores=${CORES}" \
        "memory=${RAM}" \
        "net0=virtio,bridge=${BRIDGE}" \
        "ostype=${OSTYPE}" \
        "scsihw=virtio-scsi-single" \
        "agent=enabled=1" \
        "serial0=socket" \
        "vga=serial0" \
        "scsi0=${STORAGE}:0,import-from=${ISO_STORAGE}:iso/${IMG_FILE},format=qcow2" \
        "ide2=${STORAGE}:cloudinit" \
        "boot=order=scsi0" \
        "ipconfig0=ip=${IP}/${CIDR},gw=${GATEWAY}" \
        "nameserver=${DNS_SERVER:-${GATEWAY}}" \
        "ciuser=${LINUX_USER}" \
        "cipassword=${LINUX_PASSWORD}"; then
        err "  Echec creation VM $VMID"
        return 1
    fi

    # Resize disk
    api_resize_disk "$VMID" "scsi0" "${DISK}G"

    # Upload custom cloud-init snippet if post-install exists
    if [[ -n "$POST_INSTALL" ]]; then
        local TEMPLATE
        TEMPLATE=$(get_image_template "$OS_KEY" "$IMAGES_CONF")
        local TEMPLATE_PATH="${SCRIPT_DIR}/../templates/cloud-init/${TEMPLATE}"

        if [[ -f "$TEMPLATE_PATH" ]]; then
            local USERDATA="${WORK_DIR}/cloud-init/${HOSTNAME}-user-data.yaml"
            mkdir -p "${WORK_DIR}/cloud-init"

            bash "${SCRIPT_DIR}/lib/gen-cloud-init.sh" \
                "$TEMPLATE_PATH" "$USERDATA" \
                "$HOSTNAME" "$IP" "$LINUX_USER" "$LINUX_PASSWORD" \
                "$POST_INSTALL" "$DNS_SERVER"

            # Try to upload as snippet
            if api_upload_file "$ISO_STORAGE" "snippets" "$USERDATA" 2>/dev/null; then
                api_set_vm "$VMID" "cicustom=user=${ISO_STORAGE}:snippets/${HOSTNAME}-user-data.yaml"
                log "  Custom cloud-init uploaded"
            else
                warn "  Snippet upload failed. Post-install must be run manually."
            fi
        fi
    fi

    # Start
    if [[ "${AUTO_START:-yes}" == "yes" ]]; then
        api_start_vm "$VMID"
    fi

    log "  VM ${VMID} (${HOSTNAME}) created — IP: ${IP}"
}

create_windows_vm_api() {
    local VMID="$1" HOSTNAME="$2" OS_KEY="$3" IP_SUFFIX="$4"
    local CORES="$5" RAM="$6" DISK="$7" POST_INSTALL="$8"

    local IP="${SUBNET}.${IP_SUFFIX}"
    local IMG_FILE OSTYPE TEMPLATE
    IMG_FILE=$(get_image_file "$OS_KEY" "$IMAGES_CONF")
    OSTYPE=$(get_image_ostype "$OS_KEY" "$IMAGES_CONF")
    TEMPLATE=$(get_image_template "$OS_KEY" "$IMAGES_CONF")

    echo ""
    echo "  Creating Windows VM ${VMID} (${HOSTNAME}) — ${OS_KEY}..."

    # Determine BIOS config
    local BIOS_PARAMS=()
    case "$OS_KEY" in
        win-server-2022|win-11)
            BIOS_PARAMS=(
                "bios=ovmf"
                "machine=pc-q35-8.1"
                "efidisk0=${STORAGE}:1,efitype=4m,pre-enrolled-keys=1"
                "tpmstate0=${STORAGE}:1,version=v2.0"
            )
            ;;
        win-server-2019|win-server-2016|win-10)
            BIOS_PARAMS=(
                "bios=ovmf"
                "machine=pc-q35-8.1"
                "efidisk0=${STORAGE}:1,efitype=4m,pre-enrolled-keys=0"
            )
            ;;
        *)
            BIOS_PARAMS=(
                "bios=seabios"
                "machine=pc-i440fx-8.1"
            )
            ;;
    esac

    # Create VM
    if ! api_create_vm "$VMID" \
        "name=${HOSTNAME}" \
        "cores=${CORES}" \
        "memory=${RAM}" \
        "net0=virtio,bridge=${BRIDGE}" \
        "ostype=${OSTYPE}" \
        "scsihw=virtio-scsi-single" \
        "agent=enabled=1" \
        "scsi0=${STORAGE}:${DISK},format=qcow2" \
        "${BIOS_PARAMS[@]}"; then
        err "  Echec creation VM $VMID"
        return 1
    fi

    # Attach Windows ISO
    if api_file_exists "$ISO_STORAGE" "iso" "$IMG_FILE"; then
        api_set_vm "$VMID" "cdrom=${ISO_STORAGE}:iso/${IMG_FILE}"
    else
        warn "  ISO $IMG_FILE manquant"
    fi

    # Attach VirtIO drivers
    if api_file_exists "$ISO_STORAGE" "iso" "virtio-win.iso"; then
        api_set_vm "$VMID" "ide0=${ISO_STORAGE}:iso/virtio-win.iso,media=cdrom"
    fi

    # Generate and upload autounattend ISO
    if [[ -n "$TEMPLATE" ]]; then
        local TEMPLATE_PATH="${SCRIPT_DIR}/../templates/autounattend/${TEMPLATE}"
        if [[ -f "$TEMPLATE_PATH" ]]; then
            local UNATTEND_DIR="${WORK_DIR}/autounattend/${HOSTNAME}"
            local UNATTEND_ISO="${WORK_DIR}/autounattend/${HOSTNAME}.iso"

            bash "${SCRIPT_DIR}/lib/gen-autounattend.sh" \
                "$TEMPLATE_PATH" "$UNATTEND_DIR" \
                "$HOSTNAME" "$IP" "${SUBNET}.0" "255.255.255.0" "$GATEWAY" \
                "${DNS_SERVER:-${GATEWAY}}" "$WINDOWS_ADMIN_PASSWORD" \
                "$OS_KEY" "$POST_INSTALL"

            # Create ISO
            if command -v genisoimage &>/dev/null; then
                genisoimage -quiet -o "$UNATTEND_ISO" -J -r "$UNATTEND_DIR" 2>/dev/null
            elif command -v mkisofs &>/dev/null; then
                mkisofs -quiet -o "$UNATTEND_ISO" -J -r "$UNATTEND_DIR" 2>/dev/null
            else
                warn "  genisoimage/mkisofs requis pour l'autounattend."
                warn "  apt install genisoimage"
            fi

            # Upload autounattend ISO to Proxmox
            if [[ -f "$UNATTEND_ISO" ]]; then
                local ISO_NAME="autounattend-${HOSTNAME}.iso"
                api_upload_file "$ISO_STORAGE" "iso" "$UNATTEND_ISO"
                api_set_vm "$VMID" "ide2=${ISO_STORAGE}:iso/${ISO_NAME},media=cdrom"
                log "  Autounattend ISO uploaded"
            fi
        fi
    fi

    # Boot order: CD first
    api_set_vm "$VMID" "boot=order=cdrom;scsi0"

    # Start
    if [[ "${AUTO_START:-yes}" == "yes" ]]; then
        api_start_vm "$VMID"
    fi

    log "  VM ${VMID} (${HOSTNAME}) created — IP: ${IP}"
}

# --- Main loop ---
create_vm_from_csv_api() {
    local vmid="$1" hostname="$2" os_key="$3" ip_suffix="$4"
    local cores="$5" ram="$6" disk="$7" post_install="$8"

    local vm_type
    vm_type=$(get_image_type "$os_key" "$IMAGES_CONF")

    if [[ "$vm_type" == "linux" ]]; then
        if create_linux_vm_api "$vmid" "$hostname" "$os_key" "$ip_suffix" \
                               "$cores" "$ram" "$disk" "$post_install"; then
            CREATED_LINUX=$((CREATED_LINUX + 1))
        else
            FAILED=$((FAILED + 1))
        fi
    elif [[ "$vm_type" == "windows" ]]; then
        if create_windows_vm_api "$vmid" "$hostname" "$os_key" "$ip_suffix" \
                                  "$cores" "$ram" "$disk" "$post_install"; then
            CREATED_WINDOWS=$((CREATED_WINDOWS + 1))
        else
            FAILED=$((FAILED + 1))
        fi
    else
        err "Type inconnu pour $os_key"
        FAILED=$((FAILED + 1))
    fi
}

parse_vms "$VMS_CSV" create_vm_from_csv_api

# ==============================================================================
# PHASE 4 — SUMMARY
# ==============================================================================
step "Resume"

echo ""
echo "Crees : $CREATED_LINUX Linux + $CREATED_WINDOWS Windows"
[[ $FAILED -gt 0 ]] && err "Echecs : $FAILED"
echo ""
echo "Prochaines etapes:"
echo "  1. Attendre les VMs Linux (~5 min cloud-init)"
echo "  2. Attendre les VMs Windows (~30-60 min autounattend)"
echo "  3. Lancer l'orchestration: bash orchestrate-lab-api.sh demo"
echo "  4. Verifier: bash verify-lab.sh demo"
echo ""
echo "=== Setup API termine ==="
