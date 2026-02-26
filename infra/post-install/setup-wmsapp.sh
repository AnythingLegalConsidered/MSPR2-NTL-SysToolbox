#!/bin/bash
# ==============================================================================
# NTL-SysToolbox — Post-install WMS-APP (Ubuntu 20.04)
# ==============================================================================
# Installs Nginx as a simple WMS application front-end.
# Shows a status page linking to WMS-DB backend.
#
# Executed via cloud-init runcmd on first boot.
# ==============================================================================

set -euo pipefail

echo "=== NTL-SysToolbox — Setup WMS-APP ==="

WMS_DB_IP="192.168.10.21"

# --- Step 1: Install packages ---
echo "[1/3] Installation de nginx..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nginx curl > /dev/null 2>&1

# --- Step 2: Create WMS landing page ---
echo "[2/3] Creation de la page WMS..."

cat > /var/www/html/index.html << 'HTML'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>NTL WMS Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .ok { background: #d4edda; color: #155724; }
        .info { background: #d1ecf1; color: #0c5460; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        td { padding: 8px; border-bottom: 1px solid #eee; }
        td:first-child { font-weight: bold; color: #555; }
    </style>
</head>
<body>
    <div class="container">
        <h1>NordTransit Logistics — WMS v1.0</h1>
        <div class="status ok">Application operationnelle</div>
        <div class="status info">Warehouse Management System — Hauts-de-France</div>
        <table>
            <tr><td>Backend</td><td>WMS-DB (192.168.10.21:3306)</td></tr>
            <tr><td>Base de donnees</td><td>wms (MySQL)</td></tr>
            <tr><td>Entrepots</td><td>WH1-Lens, WH2-Valenciennes, WH3-Arras</td></tr>
            <tr><td>Serveur</td><td>WMS-APP (192.168.10.22)</td></tr>
        </table>
    </div>
</body>
</html>
HTML

# --- Step 3: Enable and start nginx ---
echo "[3/3] Activation de nginx..."
systemctl enable nginx
systemctl restart nginx

echo "=== WMS-APP Setup termine (HTTP port 80) ==="
