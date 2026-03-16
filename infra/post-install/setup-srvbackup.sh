#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Post-install SRV-BACKUP (Ubuntu 16.04)
# ==============================================================================
# Configures automated MySQL backup from WMS-DB.
# Cron job runs daily at 02:00.
#
# Executed via cloud-init runcmd on first boot.
# ==============================================================================

set -euo pipefail

echo "=== NTL-SysToolbox — Setup SRV-BACKUP ==="

WMS_DB_IP="192.168.10.21"
MYSQL_USER="wms_user"
MYSQL_PASSWORD="WmsP@ss2026"
MYSQL_DB="wms"
BACKUP_DIR="/var/backups/wms"

# --- Step 1: Install packages ---
echo "[1/4] Installation mysql-client..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq mysql-client cron > /dev/null 2>&1

# --- Step 2: Create backup directory and script ---
echo "[2/4] Creation du script de backup..."
mkdir -p "$BACKUP_DIR"

cat > /opt/backup-wms.sh << SCRIPT
#!/bin/bash
# NTL WMS Database Backup — automated by SRV-BACKUP
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/wms_\${TIMESTAMP}.sql"
LOG_FILE="${BACKUP_DIR}/backup.log"

echo "[\${TIMESTAMP}] Starting backup..." >> "\$LOG_FILE"

mysqldump -h ${WMS_DB_IP} -u ${MYSQL_USER} -p'${MYSQL_PASSWORD}' ${MYSQL_DB} > "\$BACKUP_FILE" 2>> "\$LOG_FILE"

if [[ \$? -eq 0 ]]; then
    SIZE=\$(du -h "\$BACKUP_FILE" | cut -f1)
    SHA=\$(sha256sum "\$BACKUP_FILE" | cut -d' ' -f1)
    echo "[\${TIMESTAMP}] OK — \$BACKUP_FILE (\$SIZE, sha256:\$SHA)" >> "\$LOG_FILE"
else
    echo "[\${TIMESTAMP}] ERREUR — backup echoue" >> "\$LOG_FILE"
fi

# Cleanup: keep last 7 days
find ${BACKUP_DIR} -name "wms_*.sql" -mtime +7 -delete 2>/dev/null
SCRIPT

chmod +x /opt/backup-wms.sh

# --- Step 3: Configure cron ---
echo "[3/4] Configuration du cron job..."

# Add daily backup at 02:00
CRON_ENTRY="0 2 * * * /opt/backup-wms.sh"
(crontab -l 2>/dev/null | grep -v "backup-wms.sh"; echo "$CRON_ENTRY") | crontab -

systemctl enable cron
systemctl restart cron

echo "  Cron: $CRON_ENTRY"

# --- Step 4: Wait for MySQL and run first backup ---
echo "[4/4] Premier backup..."

RETRIES=0
MAX_RETRIES=20
while [[ $RETRIES -lt $MAX_RETRIES ]]; do
    if timeout 2 bash -c "echo > /dev/tcp/${WMS_DB_IP}/3306" 2>/dev/null; then
        echo "  MySQL accessible sur ${WMS_DB_IP}:3306"
        /opt/backup-wms.sh
        echo "  Premier backup termine"
        break
    fi
    RETRIES=$((RETRIES + 1))
    echo "  Attente MySQL ($RETRIES/$MAX_RETRIES)..."
    sleep 15
done

if [[ $RETRIES -ge $MAX_RETRIES ]]; then
    echo "  WARN: MySQL non accessible — le backup tournera via cron"
fi

echo "=== SRV-BACKUP Setup termine ==="
echo "  Backups: $BACKUP_DIR"
echo "  Cron: tous les jours a 02:00"
