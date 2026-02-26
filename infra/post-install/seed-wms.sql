-- ==============================================================================
-- NTL-SysToolbox — WMS Database Schema + Demo Data
-- ==============================================================================
-- Run on WMS-DB after MySQL install:
--   mysql -u root < seed-wms.sql
--
-- Or via SSH from the client:
--   ssh sysadmin@192.168.10.21 'mysql -u root' < seed-wms.sql
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS wms;
USE wms;

-- Shipments table
CREATE TABLE IF NOT EXISTS shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_number VARCHAR(50) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    status ENUM('pending', 'in_transit', 'delivered') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(30) NOT NULL,
    warehouse VARCHAR(10) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Demo data — shipments
INSERT INTO shipments (tracking_number, origin, destination, status) VALUES
('NTL-2026-001', 'WH1-Lens', 'Client-Paris', 'delivered'),
('NTL-2026-002', 'WH2-Valenciennes', 'Client-Lyon', 'in_transit'),
('NTL-2026-003', 'WH3-Arras', 'Client-Marseille', 'pending'),
('NTL-2026-004', 'WH1-Lens', 'Client-Lille', 'delivered'),
('NTL-2026-005', 'WH2-Valenciennes', 'Client-Bordeaux', 'in_transit'),
('NTL-2026-006', 'WH3-Arras', 'Client-Strasbourg', 'pending'),
('NTL-2026-007', 'WH1-Lens', 'Client-Nantes', 'delivered'),
('NTL-2026-008', 'WH2-Valenciennes', 'Client-Toulouse', 'in_transit');

-- Demo data — inventory
INSERT INTO inventory (product_code, warehouse, quantity) VALUES
('SKU-A100', 'WH1', 250),
('SKU-B200', 'WH2', 180),
('SKU-C300', 'WH3', 420),
('SKU-D400', 'WH1', 95),
('SKU-E500', 'WH2', 310),
('SKU-F600', 'WH3', 150);

-- Application user (not root!)
CREATE USER IF NOT EXISTS 'wms_user'@'%' IDENTIFIED BY 'WmsP@ss2026';
GRANT ALL PRIVILEGES ON wms.* TO 'wms_user'@'%';
FLUSH PRIVILEGES;

-- Verify
SELECT 'shipments' AS tbl, COUNT(*) AS rows_count FROM shipments
UNION ALL
SELECT 'inventory', COUNT(*) FROM inventory;
