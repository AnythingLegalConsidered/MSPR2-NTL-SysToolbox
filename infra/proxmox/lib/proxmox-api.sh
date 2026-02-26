#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Proxmox API wrapper
# ==============================================================================
# Provides functions that mirror `qm` commands but use the REST API.
# Works from any machine with curl (deployer VM, laptop, etc.)
#
# Required env vars (from config.local.env):
#   PVE_HOST        — https://proxmox.lab.loc:8006
#   PVE_NODE        — pve (or your node name)
#   PVE_TOKEN_ID    — user@pam!token-name
#   PVE_TOKEN_SECRET — the token secret
#   STORAGE         — local-lvm
#   ISO_STORAGE     — local
# ==============================================================================

# --- Validate API config ---
pve_check_config() {
    local missing=0
    for var in PVE_HOST PVE_NODE PVE_TOKEN_ID PVE_TOKEN_SECRET; do
        if [[ -z "${!var}" ]]; then
            err "Variable $var requise pour le mode API. Remplissez config.local.env."
            missing=$((missing + 1))
        fi
    done
    [[ $missing -gt 0 ]] && return 1
    return 0
}

# --- Raw API call ---
# Usage: pve_api <method> <endpoint> [data...]
# Example: pve_api GET /nodes/pve/qemu
# Example: pve_api POST /nodes/pve/qemu --data-urlencode "vmid=1010" --data-urlencode "name=DC01"
pve_api() {
    local method="$1"
    local endpoint="$2"
    shift 2

    local url="${PVE_HOST}/api2/json${endpoint}"
    local auth="Authorization: PVEAPIToken=${PVE_TOKEN_ID}=${PVE_TOKEN_SECRET}"

    local result
    result=$(curl -s -k -X "$method" \
        -H "$auth" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        "$@" \
        "$url" 2>&1)

    local code=$?
    if [[ $code -ne 0 ]]; then
        err "API call failed: curl exit $code"
        return 1
    fi

    # Check for API errors
    local errors
    errors=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('errors',''))" 2>/dev/null)
    if [[ -n "$errors" && "$errors" != "None" && "$errors" != "" ]]; then
        err "API error: $errors"
        return 1
    fi

    echo "$result"
}

# --- Convenience: extract .data from API response ---
pve_api_data() {
    pve_api "$@" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin).get('data','')))" 2>/dev/null
}

# --- Wait for API task to complete ---
# Proxmox async operations return an UPID that we need to poll
pve_wait_task() {
    local upid="$1"
    local timeout="${2:-120}"
    local elapsed=0

    # Extract UPID from JSON response if needed
    upid=$(echo "$upid" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    print(d.get('data',''))
except:
    print(sys.stdin.read().strip())
" 2>/dev/null)

    [[ -z "$upid" || "$upid" == "None" ]] && return 0

    while [[ $elapsed -lt $timeout ]]; do
        local status
        status=$(pve_api GET "/nodes/${PVE_NODE}/tasks/${upid}/status" 2>/dev/null)
        local task_status
        task_status=$(echo "$status" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null)

        if [[ "$task_status" == "stopped" ]]; then
            local exitstatus
            exitstatus=$(echo "$status" | python3 -c "import sys,json; print(json.load(sys.stdin)['data'].get('exitstatus','OK'))" 2>/dev/null)
            if [[ "$exitstatus" == "OK" ]]; then
                return 0
            else
                err "Task failed: $exitstatus"
                return 1
            fi
        fi

        sleep 3
        elapsed=$((elapsed + 3))
    done

    warn "Task timeout after ${timeout}s: $upid"
    return 1
}

# ==============================================================================
# VM OPERATIONS (mirror qm commands)
# ==============================================================================

# Check if VM exists
# Usage: api_vm_exists <vmid>
api_vm_exists() {
    local vmid="$1"
    local result
    result=$(pve_api GET "/nodes/${PVE_NODE}/qemu/${vmid}/status/current" 2>/dev/null)
    echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('status',''))" 2>/dev/null | grep -q .
}

# Get VM status
# Usage: api_vm_status <vmid> → "running" / "stopped"
api_vm_status() {
    local vmid="$1"
    pve_api GET "/nodes/${PVE_NODE}/qemu/${vmid}/status/current" 2>/dev/null | \
        python3 -c "import sys,json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null
}

# Create VM
# Usage: api_create_vm <vmid> <params...>
# Params are key=value pairs: name=DC01 cores=2 memory=4096 etc.
api_create_vm() {
    local vmid="$1"
    shift

    local data_args=("--data-urlencode" "vmid=${vmid}")
    for param in "$@"; do
        data_args+=("--data-urlencode" "$param")
    done

    local result
    result=$(pve_api POST "/nodes/${PVE_NODE}/qemu" "${data_args[@]}")
    pve_wait_task "$result"
}

# Set VM configuration
# Usage: api_set_vm <vmid> <key=value...>
api_set_vm() {
    local vmid="$1"
    shift

    local data_args=()
    for param in "$@"; do
        data_args+=("--data-urlencode" "$param")
    done

    local result
    result=$(pve_api PUT "/nodes/${PVE_NODE}/qemu/${vmid}/config" "${data_args[@]}")
}

# Resize VM disk
# Usage: api_resize_disk <vmid> <disk> <size>
api_resize_disk() {
    local vmid="$1" disk="$2" size="$3"
    pve_api PUT "/nodes/${PVE_NODE}/qemu/${vmid}/resize" \
        --data-urlencode "disk=${disk}" \
        --data-urlencode "size=${size}" >/dev/null
}

# Start VM
# Usage: api_start_vm <vmid>
api_start_vm() {
    local vmid="$1"
    local result
    result=$(pve_api POST "/nodes/${PVE_NODE}/qemu/${vmid}/status/start")
    pve_wait_task "$result" 30
}

# Stop VM (graceful)
# Usage: api_stop_vm <vmid> [timeout]
api_stop_vm() {
    local vmid="$1" timeout="${2:-60}"
    local result
    result=$(pve_api POST "/nodes/${PVE_NODE}/qemu/${vmid}/status/shutdown" \
        --data-urlencode "timeout=${timeout}")
    pve_wait_task "$result" "$((timeout + 10))"
}

# Force stop VM
# Usage: api_force_stop_vm <vmid>
api_force_stop_vm() {
    local vmid="$1"
    pve_api POST "/nodes/${PVE_NODE}/qemu/${vmid}/status/stop" >/dev/null
}

# Snapshot VM
# Usage: api_snapshot_vm <vmid> <name> <description>
api_snapshot_vm() {
    local vmid="$1" name="$2" desc="${3:-}"
    local result
    result=$(pve_api POST "/nodes/${PVE_NODE}/qemu/${vmid}/snapshot" \
        --data-urlencode "snapname=${name}" \
        --data-urlencode "description=${desc}")
    pve_wait_task "$result" 120
}

# Delete VM
# Usage: api_delete_vm <vmid>
api_delete_vm() {
    local vmid="$1"
    local result
    result=$(pve_api DELETE "/nodes/${PVE_NODE}/qemu/${vmid}")
    pve_wait_task "$result" 60
}

# ==============================================================================
# STORAGE OPERATIONS
# ==============================================================================

# Upload a file to Proxmox storage (ISO/snippets)
# Usage: api_upload_file <storage> <content_type> <file_path>
# content_type: iso, snippets, vztmpl
api_upload_file() {
    local storage="$1" content="$2" filepath="$3"
    local filename
    filename=$(basename "$filepath")

    local result
    result=$(curl -s -k \
        -H "Authorization: PVEAPIToken=${PVE_TOKEN_ID}=${PVE_TOKEN_SECRET}" \
        -F "content=${content}" \
        -F "filename=@${filepath}" \
        "${PVE_HOST}/api2/json/nodes/${PVE_NODE}/storage/${storage}/upload" 2>&1)

    local upid
    upid=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',''))" 2>/dev/null)
    if [[ -n "$upid" && "$upid" != "None" ]]; then
        pve_wait_task "$result" 300
    fi
}

# Download a file from URL directly to Proxmox storage
# Usage: api_download_url <storage> <url> <filename> <content_type>
api_download_url() {
    local storage="$1" url="$2" filename="$3" content="${4:-iso}"

    local result
    result=$(pve_api POST "/nodes/${PVE_NODE}/storage/${storage}/download-url" \
        --data-urlencode "url=${url}" \
        --data-urlencode "filename=${filename}" \
        --data-urlencode "content=${content}")
    pve_wait_task "$result" 600
}

# List files in storage
# Usage: api_list_storage <storage> <content_type>
api_list_storage() {
    local storage="$1" content="${2:-iso}"
    pve_api GET "/nodes/${PVE_NODE}/storage/${storage}/content?content=${content}" | \
        python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', [])
for item in data:
    print(item.get('volid', ''))
" 2>/dev/null
}

# Check if a file exists in storage
# Usage: api_file_exists <storage> <content> <filename>
api_file_exists() {
    local storage="$1" content="$2" filename="$3"
    api_list_storage "$storage" "$content" | grep -q "$filename"
}

# ==============================================================================
# NODE OPERATIONS
# ==============================================================================

# Get node status (RAM, CPU, storage)
api_node_status() {
    pve_api_data GET "/nodes/${PVE_NODE}/status"
}

# List all VMs on node
api_list_vms() {
    pve_api GET "/nodes/${PVE_NODE}/qemu" | \
        python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', [])
for vm in sorted(data, key=lambda x: x.get('vmid', 0)):
    print(f\"{vm['vmid']}\t{vm.get('name','')}\t{vm.get('status','')}\")
" 2>/dev/null
}

# ==============================================================================
# NETWORK OPERATIONS (bridge check via API)
# ==============================================================================

# List network interfaces on node
api_list_networks() {
    pve_api GET "/nodes/${PVE_NODE}/network" | \
        python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', [])
for iface in data:
    print(f\"{iface.get('iface','')}\t{iface.get('type','')}\t{iface.get('address','')}\")
" 2>/dev/null
}

# Check if bridge exists
api_bridge_exists() {
    local bridge="$1"
    api_list_networks | grep -q "^${bridge}"
}

# Create bridge (requires sufficient permissions)
api_create_bridge() {
    local bridge="$1" address="$2" cidr="$3"
    pve_api POST "/nodes/${PVE_NODE}/network" \
        --data-urlencode "iface=${bridge}" \
        --data-urlencode "type=bridge" \
        --data-urlencode "cidr=${address}/${cidr}" \
        --data-urlencode "bridge_ports=none" \
        --data-urlencode "bridge_stp=off" \
        --data-urlencode "bridge_fd=0" \
        --data-urlencode "autostart=1" >/dev/null

    # Apply network changes
    pve_api PUT "/nodes/${PVE_NODE}/network" >/dev/null
}
