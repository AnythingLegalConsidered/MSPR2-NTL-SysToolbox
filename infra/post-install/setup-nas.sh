#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Post-install NAS-01 (Debian 10)
# ==============================================================================
# Configures NFS and SMB exports for backup storage.
# Target directory: /backup/wms (accessible from 192.168.10.0/24)
#
# Executed via cloud-init runcmd on first boot.
# ==============================================================================

set -euo pipefail

echo "=== NTL-SysToolbox — Setup NAS-01 ==="

SUBNET="192.168.10.0/24"
BACKUP_DIR="/backup/wms"

# --- Step 1: Install packages ---
echo "[1/4] Installation NFS + Samba..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nfs-kernel-server samba > /dev/null 2>&1

# --- Step 2: Create backup directories ---
echo "[2/4] Creation des repertoires..."
mkdir -p "$BACKUP_DIR"
mkdir -p /backup/archives
chmod 777 "$BACKUP_DIR"
chmod 777 /backup/archives

# --- Step 3: Configure NFS ---
echo "[3/4] Configuration NFS..."

# Add exports if not already present
if ! grep -q "$BACKUP_DIR" /etc/exports 2>/dev/null; then
    cat >> /etc/exports << EOF
# NTL Lab — Backup exports
${BACKUP_DIR} ${SUBNET}(rw,sync,no_subtree_check,no_root_squash)
/backup/archives ${SUBNET}(ro,sync,no_subtree_check)
EOF
fi

exportfs -ra
systemctl enable nfs-kernel-server
systemctl restart nfs-kernel-server

echo "  NFS exports:"
exportfs -v

# --- Step 4: Configure Samba ---
echo "[4/4] Configuration Samba..."

# Backup original config
cp /etc/samba/smb.conf /etc/samba/smb.conf.bak 2>/dev/null || true

cat > /etc/samba/smb.conf << 'EOF'
[global]
   workgroup = NTL
   server string = NAS-01 NordTransit Backup
   security = user
   map to guest = Bad User
   guest account = nobody

[backup]
   path = /backup/wms
   comment = NTL WMS Backup Share
   browseable = yes
   read only = no
   guest ok = yes
   create mask = 0666
   directory mask = 0777

[archives]
   path = /backup/archives
   comment = NTL Archived Backups
   browseable = yes
   read only = yes
   guest ok = yes
EOF

systemctl enable smbd
systemctl restart smbd

echo "=== NAS-01 Setup termine ==="
echo "  NFS: mount -t nfs 192.168.10.40:${BACKUP_DIR} /mnt"
echo "  SMB: \\\\192.168.10.40\\backup"
