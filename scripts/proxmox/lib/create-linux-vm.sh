#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Create a Linux VM with cloud-init
# ==============================================================================
# Called by setup-lab.sh for each Linux entry in vms.csv.
# Not meant to be run standalone.
# ==============================================================================

create_linux_vm() {
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

    local IMG_PATH="${ISO_PATH}/${IMG_FILE}"

    echo "  Creating Linux VM ${VMID} (${HOSTNAME}) — ${OS_KEY}..."

    if [[ ! -f "$IMG_PATH" ]]; then
        err "  Cloud image not found: $IMG_PATH"
        err "  Run download-images.sh first."
        return 1
    fi

    # Create VM
    run_cmd qm create "$VMID" \
        --name "$HOSTNAME" \
        --cores "$CORES" \
        --memory "$RAM" \
        --net0 "virtio,bridge=${BRIDGE}" \
        --ostype "$OSTYPE" \
        --scsihw virtio-scsi-single \
        --agent enabled=1 \
        --serial0 socket \
        --vga serial0

    # Import cloud image as disk
    run_cmd qm importdisk "$VMID" "$IMG_PATH" "$STORAGE" --format qcow2
    run_cmd qm set "$VMID" --scsi0 "${STORAGE}:vm-${VMID}-disk-0"

    # Resize disk
    run_cmd qm resize "$VMID" scsi0 "${DISK}G"

    # Cloud-init drive
    run_cmd qm set "$VMID" --ide2 "${STORAGE}:cloudinit"

    # Boot order
    run_cmd qm set "$VMID" --boot order=scsi0

    # Cloud-init basic config
    run_cmd qm set "$VMID" \
        --ipconfig0 "ip=${IP}/${CIDR},gw=${GATEWAY}" \
        --nameserver "${DNS_SERVER:-${GATEWAY}}" \
        --ciuser "$LINUX_USER" \
        --cipassword "$LINUX_PASSWORD"

    # Custom cloud-init user-data (if snippet storage is available)
    if [[ -n "$TEMPLATE" ]]; then
        local TEMPLATE_PATH="${SCRIPT_DIR}/../templates/cloud-init/${TEMPLATE}"
        if [[ -f "$TEMPLATE_PATH" ]]; then
            # Generate personalized user-data
            local USERDATA="${WORK_DIR}/cloud-init/${HOSTNAME}-user-data.yaml"
            mkdir -p "${WORK_DIR}/cloud-init"

            bash "${SCRIPT_DIR}/lib/gen-cloud-init.sh" \
                "$TEMPLATE_PATH" "$USERDATA" \
                "$HOSTNAME" "$IP" "$LINUX_USER" "$LINUX_PASSWORD" \
                "$POST_INSTALL" "$DNS_SERVER"

            # Try to use Proxmox snippets
            local SNIPPET_STORAGE
            SNIPPET_STORAGE=$(pvesm status --content snippets 2>/dev/null | awk 'NR>1{print $1; exit}')

            if [[ -n "$SNIPPET_STORAGE" ]]; then
                local SNIPPET_PATH
                SNIPPET_PATH=$(pvesm path "${SNIPPET_STORAGE}:snippets/" 2>/dev/null || echo "")
                if [[ -d "${SNIPPET_PATH%/}" ]]; then
                    cp "$USERDATA" "${SNIPPET_PATH%/}/${HOSTNAME}-user-data.yaml"
                    run_cmd qm set "$VMID" --cicustom "user=${SNIPPET_STORAGE}:snippets/${HOSTNAME}-user-data.yaml"
                    log "  Custom cloud-init applied"
                fi
            else
                warn "  No snippet storage. Basic cloud-init only."
                [[ -n "$POST_INSTALL" ]] && warn "  Post-install script must be run manually via SSH."
            fi
        fi
    fi

    # Start
    if [[ "$AUTO_START" == "yes" ]]; then
        run_cmd qm start "$VMID"
    fi

    log "  VM ${VMID} (${HOSTNAME}) created — IP: ${IP}"
}
