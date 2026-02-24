#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Create a Windows VM with autounattend
# ==============================================================================
# Called by setup-lab.sh for each Windows entry in vms.csv.
# ==============================================================================

create_windows_vm() {
    local VMID="$1"
    local HOSTNAME="$2"
    local OS_KEY="$3"
    local IP_SUFFIX="$4"
    local CORES="$5"
    local RAM="$6"
    local DISK="$7"
    local POST_INSTALL="$8"

    local IP="${SUBNET}.${IP_SUFFIX}"
    local IMG_FILE
    IMG_FILE=$(get_image_file "$OS_KEY" "$IMAGES_CONF")
    local OSTYPE
    OSTYPE=$(get_image_ostype "$OS_KEY" "$IMAGES_CONF")
    local TEMPLATE
    TEMPLATE=$(get_image_template "$OS_KEY" "$IMAGES_CONF")

    echo "  Creating Windows VM ${VMID} (${HOSTNAME}) — ${OS_KEY}..."

    # Check ISO exists
    if [[ ! -f "${ISO_PATH}/${IMG_FILE}" ]]; then
        warn "  ISO not found: ${IMG_FILE}"
        warn "  VM will be created but cannot boot. Upload the ISO and retry."
    fi

    # Determine BIOS type based on OS version
    local BIOS_ARGS=""
    case "$OS_KEY" in
        win-server-2022|win-11)
            # Modern OS: UEFI + TPM required
            BIOS_ARGS="--bios ovmf --machine pc-q35-8.1 --efidisk0 ${STORAGE}:1,efitype=4m,pre-enrolled-keys=1 --tpmstate0 ${STORAGE}:1,version=v2.0"
            ;;
        win-server-2019|win-server-2016|win-10)
            # Modern OS: UEFI preferred but no TPM required
            BIOS_ARGS="--bios ovmf --machine pc-q35-8.1 --efidisk0 ${STORAGE}:1,efitype=4m,pre-enrolled-keys=0"
            ;;
        *)
            # Legacy OS (2012 R2, 2008 R2, Win 7): SeaBIOS
            BIOS_ARGS="--bios seabios --machine pc-i440fx-8.1"
            ;;
    esac

    # Create VM
    run_cmd qm create "$VMID" \
        --name "$HOSTNAME" \
        --cores "$CORES" \
        --memory "$RAM" \
        --net0 "virtio,bridge=${BRIDGE}" \
        --ostype "$OSTYPE" \
        --scsihw virtio-scsi-single \
        --agent enabled=1 \
        $BIOS_ARGS

    # System disk
    run_cmd qm set "$VMID" --scsi0 "${STORAGE}:${DISK},format=qcow2"

    # Attach Windows ISO as CD
    if [[ -f "${ISO_PATH}/${IMG_FILE}" ]]; then
        run_cmd qm set "$VMID" --cdrom "${ISO_STORAGE}:iso/${IMG_FILE}"
    fi

    # Attach VirtIO drivers
    if [[ -f "${ISO_PATH}/virtio-win.iso" ]]; then
        run_cmd qm set "$VMID" --ide0 "${ISO_STORAGE}:iso/virtio-win.iso,media=cdrom"
    else
        warn "  VirtIO ISO not found. Windows may not detect disks."
    fi

    # Generate autounattend ISO
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

            # Create ISO from the autounattend directory
            if command -v genisoimage &>/dev/null; then
                genisoimage -quiet -o "$UNATTEND_ISO" -J -r "$UNATTEND_DIR" 2>/dev/null
            elif command -v mkisofs &>/dev/null; then
                mkisofs -quiet -o "$UNATTEND_ISO" -J -r "$UNATTEND_DIR" 2>/dev/null
            else
                warn "  genisoimage/mkisofs not found. Cannot create autounattend ISO."
                warn "  Install: apt install genisoimage"
                return 0
            fi

            # Copy ISO to Proxmox storage and attach as floppy (Windows reads it)
            cp "$UNATTEND_ISO" "${ISO_PATH}/autounattend-${HOSTNAME}.iso"
            run_cmd qm set "$VMID" --ide2 "${ISO_STORAGE}:iso/autounattend-${HOSTNAME}.iso,media=cdrom"

            log "  Autounattend ISO attached"
        else
            warn "  Template not found: $TEMPLATE_PATH"
        fi
    fi

    # Boot order: CD first (for install), then disk
    run_cmd qm set "$VMID" --boot order="cdrom;scsi0"

    # Start
    if [[ "$AUTO_START" == "yes" ]]; then
        run_cmd qm start "$VMID"
    fi

    log "  VM ${VMID} (${HOSTNAME}) created — IP: ${IP} (auto-install in progress)"
}
