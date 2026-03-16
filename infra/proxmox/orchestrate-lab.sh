#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Lab Orchestrator (wave-based deployment)
# ==============================================================================
# Starts VMs in dependency order after setup-lab.sh has created them.
# Manages boot sequencing: Linux first, then DC01, then domain-dependent VMs.
#
# Usage:
#   bash orchestrate-lab.sh              # default: demo profile
#   bash orchestrate-lab.sh essential    # minimal (DC01 + WMS-DB + CLIENT-01)
#   bash orchestrate-lab.sh demo         # recommended (11 VMs)
#   bash orchestrate-lab.sh full         # all 18 VMs
#
# Prerequisites:
#   - Run as root on the Proxmox host
#   - setup-lab.sh has been run (VMs exist but may not be started)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Load config ---
CONFIG_FILE="${SCRIPT_DIR}/config.local.env"
[[ ! -f "$CONFIG_FILE" ]] && CONFIG_FILE="${SCRIPT_DIR}/config.env"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERREUR: Config introuvable. Copiez config.env vers config.local.env."
    exit 1
fi

source "$CONFIG_FILE"
source "$SCRIPT_DIR/lib/common.sh"
source "$SCRIPT_DIR/lib/wait-service.sh"

# --- Parse profile ---
PROFILE="${1:-demo}"
PROFILES_CONF="$SCRIPT_DIR/profiles.conf"
VMS_CSV="$SCRIPT_DIR/vms.csv"
IMAGES_CONF="$SCRIPT_DIR/images.conf"

if [[ ! -f "$PROFILES_CONF" ]]; then
    err "profiles.conf introuvable: $PROFILES_CONF"
    exit 1
fi

PROFILE_VMIDS=$(grep "^${PROFILE}|" "$PROFILES_CONF" | cut -d'|' -f2)
if [[ -z "$PROFILE_VMIDS" ]]; then
    err "Profil '$PROFILE' inconnu. Profils disponibles:"
    grep -v "^#" "$PROFILES_CONF" | cut -d'|' -f1 | sed 's/^/  - /'
    exit 1
fi

# Convert comma-separated to array
IFS=',' read -ra VMIDS <<< "$PROFILE_VMIDS"

echo ""
echo "=== NTL-SysToolbox — Lab Orchestrator ==="
echo "Profil  : $PROFILE (${#VMIDS[@]} VMs)"
echo "VMs     : ${PROFILE_VMIDS}"
echo "Reseau  : ${SUBNET}.0/${CIDR}"
echo ""

# Helper: check if a VMID is in the profile
in_profile() {
    local target="$1"
    for vmid in "${VMIDS[@]}"; do
        [[ "$vmid" == "$target" ]] && return 0
    done
    return 1
}

# Helper: get hostname for a VMID from vms.csv
get_hostname() {
    local target="$1"
    grep "^${target}," "$VMS_CSV" | cut -d',' -f2
}

# Helper: get OS type for a VMID
get_vm_type() {
    local target="$1"
    local os_key
    os_key=$(grep "^${target}," "$VMS_CSV" | cut -d',' -f3)
    get_image_type "$os_key" "$IMAGES_CONF"
}

# ==============================================================================
# WAVE 0 — PRE-FLIGHT
# ==============================================================================
step "Vague 0 — Pre-flight"

MISSING=0
for vmid in "${VMIDS[@]}"; do
    hostname=$(get_hostname "$vmid")
    if ! qm status "$vmid" &>/dev/null; then
        err "VM $vmid ($hostname) n'existe pas. Lancez setup-lab.sh d'abord."
        MISSING=$((MISSING + 1))
    fi
done

if [[ $MISSING -gt 0 ]]; then
    err "$MISSING VMs manquantes. Arret."
    exit 1
fi
log "Toutes les ${#VMIDS[@]} VMs existent"

# Stop all VMs first for clean sequencing (if AUTO_START was yes during setup)
echo ""
echo "Arret des VMs pour sequencement propre..."
for vmid in "${VMIDS[@]}"; do
    if qm status "$vmid" 2>/dev/null | grep -q "running"; then
        qm shutdown "$vmid" --timeout 30 2>/dev/null || qm stop "$vmid" 2>/dev/null || true
    fi
done
sleep 5

# ==============================================================================
# WAVE 1 — LINUX VMs (cloud-init, fast ~5 min)
# ==============================================================================
step "Vague 1 — VMs Linux (cloud-init)"

LINUX_STARTED=0
for vmid in "${VMIDS[@]}"; do
    vm_type=$(get_vm_type "$vmid")
    if [[ "$vm_type" == "linux" ]]; then
        hostname=$(get_hostname "$vmid")
        start_vm "$vmid" "$hostname"
        LINUX_STARTED=$((LINUX_STARTED + 1))
    fi
done

if [[ $LINUX_STARTED -gt 0 ]]; then
    echo ""
    echo "Attente cloud-init (${LINUX_STARTED} VMs Linux)..."
    sleep 30  # Initial boot delay

    # Wait for critical Linux services
    if in_profile "1021"; then
        wait_for_port "${SUBNET}.21" 22 300 "WMS-DB SSH"
        wait_for_port "${SUBNET}.21" 3306 300 "WMS-DB MySQL"
    fi
    if in_profile "1022"; then
        wait_for_port "${SUBNET}.22" 80 300 "WMS-APP HTTP"
    fi
fi

log "Vague 1 terminee ($LINUX_STARTED VMs Linux)"

# ==============================================================================
# WAVE 2 — DOMAIN CONTROLLER
# ==============================================================================
step "Vague 2 — Domain Controller"

if in_profile "1010"; then
    start_vm "1010" "DC01"
    echo ""
    echo "Attente installation Windows + promotion AD DS..."
    echo "  Cela peut prendre 30-60 minutes si DC01 n'a pas encore ete installe."
    echo "  Si DC01 est deja configure, LDAP sera detecte rapidement."
    echo ""

    # Long timeout: Windows install + AD promotion + reboot
    wait_for_port "${SUBNET}.10" 389 3600 "DC01 LDAP"

    # Also verify DNS
    wait_for_port "${SUBNET}.10" 53 60 "DC01 DNS"

    log "DC01 operationnel (AD + DNS)"
fi

# Start DC02 (its own post-install script waits for DC01)
if in_profile "1011"; then
    echo ""
    start_vm "1011" "DC02"
    echo "  DC02 lance — son post-install attend DC01 automatiquement"
fi

# ==============================================================================
# WAVE 3 — DOMAIN-DEPENDENT WINDOWS SERVERS
# ==============================================================================
step "Vague 3 — Serveurs Windows"

# These servers may need to join the domain (SRV-FILE) or just boot
WAVE3_VMIDS=(1012 1013 1015)
WAVE3_STARTED=0

for vmid in "${WAVE3_VMIDS[@]}"; do
    if in_profile "$vmid"; then
        hostname=$(get_hostname "$vmid")
        start_vm "$vmid" "$hostname"
        WAVE3_STARTED=$((WAVE3_STARTED + 1))
    fi
done

# Wait for SRV-FILE SMB if it was started
if in_profile "1012"; then
    echo ""
    echo "Attente SRV-FILE (Windows install + domain join + SMB)..."
    # Long timeout: Windows install + domain join + reboot
    wait_for_port "${SUBNET}.12" 445 3600 "SRV-FILE SMB" || true
fi

log "Vague 3 terminee ($WAVE3_STARTED serveurs Windows)"

# ==============================================================================
# WAVE 4 — WINDOWS CLIENTS
# ==============================================================================
step "Vague 4 — Clients Windows"

CLIENT_VMIDS=(1050 1051 1052 1060 1061 1062)
CLIENTS_STARTED=0

for vmid in "${CLIENT_VMIDS[@]}"; do
    if in_profile "$vmid"; then
        hostname=$(get_hostname "$vmid")
        start_vm "$vmid" "$hostname"
        CLIENTS_STARTED=$((CLIENTS_STARTED + 1))
    fi
done

log "Vague 4 terminee ($CLIENTS_STARTED clients Windows lances)"

if [[ $CLIENTS_STARTED -gt 0 ]]; then
    echo ""
    echo "Les clients Windows s'installent et joignent le domaine automatiquement."
    echo "Comptez 30-60 min pour l'install complete."
fi

# ==============================================================================
# WAVE 5 — VERIFICATION
# ==============================================================================
step "Vague 5 — Verification"

VERIFY_SCRIPT="${SCRIPT_DIR}/verify-lab.sh"
if [[ -f "$VERIFY_SCRIPT" ]]; then
    echo ""
    echo "Lancement de la verification..."
    bash "$VERIFY_SCRIPT" "$PROFILE"
else
    echo ""
    echo "verify-lab.sh non trouve. Verification manuelle:"
    echo ""

    # Quick connectivity check
    for vmid in "${VMIDS[@]}"; do
        hostname=$(get_hostname "$vmid")
        ip_suffix=$(grep "^${vmid}," "$VMS_CSV" | cut -d',' -f4)
        ip="${SUBNET}.${ip_suffix}"

        if ping -c 1 -W 2 "$ip" &>/dev/null; then
            log "  $hostname ($ip) — reachable"
        else
            warn "  $hostname ($ip) — not yet reachable"
        fi
    done
fi

# ==============================================================================
# SUMMARY
# ==============================================================================
step "Orchestration terminee"

echo ""
echo "Profil : $PROFILE"
echo "VMs    : ${#VMIDS[@]} demarrees en 5 vagues"
echo ""
echo "Prochaines etapes:"
echo "  1. Attendre que les VMs Windows terminent leur install (~30-60 min)"
echo "  2. Verifier avec: bash verify-lab.sh $PROFILE"
echo "  3. Creer des snapshots: qm snapshot <vmid> lab-ready"
echo "  4. Tester le CLI: python src/main.py"
echo ""
echo "=== Orchestration terminee ==="
