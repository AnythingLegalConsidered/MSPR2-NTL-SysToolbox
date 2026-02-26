#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Wait helpers for service dependencies
# ==============================================================================
# Reusable functions for orchestration scripts.
# Source this file: source lib/wait-service.sh
# ==============================================================================

# Wait for a TCP port to become available
# Usage: wait_for_port <ip> <port> <timeout_sec> <description>
# Returns: 0 = port open, 1 = timeout
wait_for_port() {
    local ip="$1"
    local port="$2"
    local timeout="${3:-300}"
    local desc="${4:-$ip:$port}"
    local elapsed=0
    local interval=15

    while [[ $elapsed -lt $timeout ]]; do
        if timeout 2 bash -c "echo > /dev/tcp/${ip}/${port}" 2>/dev/null; then
            log "$desc — ready ($ip:$port) [${elapsed}s]"
            return 0
        fi
        elapsed=$((elapsed + interval))
        echo "  Waiting for $desc (${elapsed}/${timeout}s)..."
        sleep "$interval"
    done

    err "$desc — timeout after ${timeout}s ($ip:$port)"
    return 1
}

# Wait for QEMU guest agent to respond
# Usage: wait_for_vm_agent <vmid> <timeout_sec>
# Returns: 0 = agent responsive, 1 = timeout
wait_for_vm_agent() {
    local vmid="$1"
    local timeout="${2:-300}"
    local elapsed=0
    local interval=10

    while [[ $elapsed -lt $timeout ]]; do
        if qm agent "$vmid" ping 2>/dev/null; then
            log "VM $vmid — guest agent ready [${elapsed}s]"
            return 0
        fi
        elapsed=$((elapsed + interval))
        sleep "$interval"
    done

    err "VM $vmid — guest agent timeout after ${timeout}s"
    return 1
}

# Wait for cloud-init to finish on a Linux VM
# Usage: wait_for_cloud_init <vmid> <timeout_sec>
# Returns: 0 = done, 1 = timeout
wait_for_cloud_init() {
    local vmid="$1"
    local timeout="${2:-600}"
    local elapsed=0
    local interval=10

    while [[ $elapsed -lt $timeout ]]; do
        if qm guest exec "$vmid" -- test -f /var/lib/cloud/instance/boot-finished 2>/dev/null; then
            log "VM $vmid — cloud-init finished [${elapsed}s]"
            return 0
        fi
        elapsed=$((elapsed + interval))
        sleep "$interval"
    done

    warn "VM $vmid — cloud-init not finished after ${timeout}s (may still be running)"
    return 1
}

# Start a VM if not already running
# Usage: start_vm <vmid> <hostname>
start_vm() {
    local vmid="$1"
    local hostname="${2:-VM $vmid}"

    if qm status "$vmid" 2>/dev/null | grep -q "running"; then
        log "$hostname ($vmid) — already running"
        return 0
    fi

    if ! qm status "$vmid" &>/dev/null; then
        err "$hostname ($vmid) — VM does not exist"
        return 1
    fi

    qm start "$vmid"
    log "$hostname ($vmid) — started"
}
