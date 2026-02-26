#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Post-install WMS-DB (Ubuntu 20.04)
# ==============================================================================
# Run this ONLY if cloud-init didn't work or for manual setup.
# If you used cloud-init (wmsdb-user-data.yaml), everything is already done.
#
# Usage (on WMS-DB via SSH or console):
#   sudo bash setup-wmsdb.sh
# ==============================================================================

set -euo pipefail

echo "=== NTL-SysToolbox — Setup WMS-DB ==="

# Check root
if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERREUR: Lancez ce script en root (sudo bash setup-wmsdb.sh)"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Install packages ---
echo "[1/6] Installation des paquets..."
apt-get update -qq
apt-get install -y -qq mysql-server openssh-server mysql-client net-tools curl

# --- Configure MySQL ---
echo "[2/6] Configuration MySQL (bind-address 0.0.0.0)..."
sed -i 's/^bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
systemctl restart mysql

# --- Import database schema + data ---
echo "[3/6] Creation BDD wms + donnees de demo..."
if [[ -f "$SCRIPT_DIR/seed-wms.sql" ]]; then
    mysql -u root < "$SCRIPT_DIR/seed-wms.sql"
else
    echo "ERREUR: seed-wms.sql introuvable dans $SCRIPT_DIR"
    echo "Copiez-le a cote de ce script et relancez."
    exit 1
fi

# --- Configure SSH ---
echo "[4/6] Configuration SSH..."
sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
systemctl restart sshd

# --- Create sysadmin user (if not exists) ---
echo "[5/6] Creation utilisateur sysadmin..."
if id "sysadmin" &>/dev/null; then
    echo "  User sysadmin existe deja."
else
    useradd -m -s /bin/bash sysadmin
    echo "sysadmin:SysAdm2026!" | chpasswd
    usermod -aG sudo sysadmin
fi

# --- Enable services on boot ---
echo "[6/6] Activation des services au boot..."
systemctl enable mysql
systemctl enable ssh

echo ""
echo "=== WMS-DB Setup termine ==="
echo "  MySQL : port 3306 (user: wms_user / WmsP@ss2026)"
echo "  SSH   : port 22   (user: sysadmin / SysAdm2026!)"
echo "  BDD   : wms (tables: shipments, inventory)"
echo ""
echo "Test rapide :"
echo "  mysql -u wms_user -p'WmsP@ss2026' wms -e 'SELECT COUNT(*) FROM shipments;'"
