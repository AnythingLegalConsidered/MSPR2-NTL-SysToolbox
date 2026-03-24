#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — MySQL Backup Script (SRV-BACKUP)
# ==============================================================================
# Backs up the WMS database from WMS-DB (192.168.10.21)
# Retention: 7 daily, 4 weekly
# ==============================================================================

set -euo pipefail

# Configuration
DB_HOST="192.168.10.21"
DB_USER="wms_user"
DB_PASS="WmsP@ss2026"
DB_NAME="wms"
BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
DAY_OF_WEEK=$(date +%u)

# Create backup
echo "[$(date)] Starting MySQL backup of ${DB_NAME}..."
DUMP_FILE="${BACKUP_DIR}/daily/${DB_NAME}_${DATE}.sql.gz"
mkdir -p "${BACKUP_DIR}/daily" "${BACKUP_DIR}/weekly"

mysqldump -h "${DB_HOST}" -u "${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" | gzip > "${DUMP_FILE}"
echo "[$(date)] Backup created: ${DUMP_FILE} ($(du -h "${DUMP_FILE}" | cut -f1))"

# Weekly copy on Sunday (day 7)
if [ "${DAY_OF_WEEK}" = "7" ]; then
    WEEKLY_FILE="${BACKUP_DIR}/weekly/${DB_NAME}_weekly_${DATE}.sql.gz"
    cp "${DUMP_FILE}" "${WEEKLY_FILE}"
    echo "[$(date)] Weekly backup: ${WEEKLY_FILE}"
fi

# Retention: keep 7 daily backups
find "${BACKUP_DIR}/daily" -name "*.sql.gz" -mtime +7 -delete
echo "[$(date)] Daily cleanup: removed backups older than 7 days"

# Retention: keep 4 weekly backups
find "${BACKUP_DIR}/weekly" -name "*.sql.gz" -mtime +28 -delete
echo "[$(date)] Weekly cleanup: removed backups older than 28 days"

echo "[$(date)] Backup complete."
