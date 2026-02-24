#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Generate cloud-init user-data from template
# ==============================================================================
# Replaces placeholders in cloud-init YAML template with VM-specific values.
#
# Usage: gen-cloud-init.sh <template> <output_file> <hostname> <ip> <user> <password> [post_install] [dns_server]
# ==============================================================================

set -euo pipefail

TEMPLATE="$1"
OUTPUT="$2"
HOSTNAME="$3"
IP="$4"
USER="$5"
PASSWORD="$6"
POST_INSTALL="${7:-}"
DNS_SERVER="${8:-}"

SCRIPT_BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# --- Build runcmd block for post-install ---
POST_INSTALL_RUNCMD=""
if [[ -n "$POST_INSTALL" && -f "${SCRIPT_BASE_DIR}/post-install/${POST_INSTALL}" ]]; then
    # Embed the post-install script content directly in cloud-init runcmd
    POST_INSTALL_RUNCMD="$(cat "${SCRIPT_BASE_DIR}/post-install/${POST_INSTALL}")"
fi

# --- Generate user-data ---
mkdir -p "$(dirname "$OUTPUT")"

sed \
    -e "s|{{HOSTNAME}}|${HOSTNAME}|g" \
    -e "s|{{IP_ADDRESS}}|${IP}|g" \
    -e "s|{{USER}}|${USER}|g" \
    -e "s|{{PASSWORD}}|${PASSWORD}|g" \
    -e "s|{{DNS_SERVER}}|${DNS_SERVER}|g" \
    "$TEMPLATE" > "$OUTPUT"

# If there's a post-install script, append it as runcmd
if [[ -n "$POST_INSTALL_RUNCMD" ]]; then
    # Check if runcmd section already exists in the output
    if grep -q "^runcmd:" "$OUTPUT"; then
        # Append commands to existing runcmd section
        echo "  # --- Post-install: ${POST_INSTALL} ---" >> "$OUTPUT"
        echo "  - |" >> "$OUTPUT"
        echo "$POST_INSTALL_RUNCMD" | sed 's/^/    /' >> "$OUTPUT"
    else
        # Add new runcmd section
        echo "" >> "$OUTPUT"
        echo "runcmd:" >> "$OUTPUT"
        echo "  # --- Post-install: ${POST_INSTALL} ---" >> "$OUTPUT"
        echo "  - |" >> "$OUTPUT"
        echo "$POST_INSTALL_RUNCMD" | sed 's/^/    /' >> "$OUTPUT"
    fi
fi

echo "  Generated: ${OUTPUT}"
