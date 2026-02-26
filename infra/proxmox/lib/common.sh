#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Shared functions
# ==============================================================================

# Colors
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
GRAY='\033[0;90m'
NC='\033[0m'

log()  { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERR]${NC} $*"; }
step() { echo -e "\n${CYAN}>>> $*${NC}"; }

run_cmd() {
    if [[ "${VERBOSE:-no}" == "yes" ]]; then
        echo -e "${GRAY}  \$ $*${NC}"
    fi
    eval "$@"
}

# --- Parse images.conf ---
# Usage: get_image_info <os_key> <field_number>
# Fields: 1=os_key 2=type 3=image_file 4=template 5=ostype
get_image_field() {
    local os_key="$1"
    local field="$2"
    local conf="$3"
    grep "^${os_key}|" "$conf" | cut -d'|' -f"$field"
}

get_image_type()     { get_image_field "$1" 2 "$2"; }
get_image_file()     { get_image_field "$1" 3 "$2"; }
get_image_template() { get_image_field "$1" 4 "$2"; }
get_image_ostype()   { get_image_field "$1" 5 "$2"; }

# --- Parse vms.csv ---
# Reads vms.csv skipping header, calls callback with fields
# Usage: parse_vms <csv_file> <callback_function>
parse_vms() {
    local csv="$1"
    local callback="$2"
    local line_num=0

    while IFS=',' read -r vmid hostname os_key ip_suffix cores ram_mb disk_gb post_install; do
        line_num=$((line_num + 1))
        [[ $line_num -eq 1 ]] && continue  # skip header
        [[ -z "$vmid" ]] && continue       # skip empty lines
        [[ "$vmid" =~ ^# ]] && continue    # skip comments

        "$callback" "$vmid" "$hostname" "$os_key" "$ip_suffix" "$cores" "$ram_mb" "$disk_gb" "$post_install"
    done < "$csv"
}

# --- Check if VM exists ---
vm_exists() {
    qm status "$1" &>/dev/null
}

# --- Deduce DNS server from vms.csv (first DC = lowest IP) ---
get_dns_server() {
    local csv="$1"
    local subnet="$2"
    # Find first windows server entry (DC01 should be first)
    local suffix
    suffix=$(grep "win-server" "$csv" | head -1 | cut -d',' -f4)
    echo "${subnet}.${suffix}"
}
