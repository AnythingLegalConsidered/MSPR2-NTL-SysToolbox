"""
NTL WMS — Warehouse Management System (Flask)
Connects to MySQL wms database on WMS-DB (192.168.10.21)
"""
import os
from flask import Flask, render_template

import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("WMS_DB_HOST", "192.168.10.21"),
    "database": os.environ.get("WMS_DB_NAME", "wms"),
    "user": os.environ.get("WMS_DB_USER", "wms_user"),
    "password": os.environ.get("WMS_DB_PASSWORD", "WmsP@ss2026"),
    "connect_timeout": 5,
}


def get_db():
    """Get a database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error:
        return None


@app.route("/")
def dashboard():
    """Dashboard — overview of shipments and inventory."""
    stats = {
        "total_shipments": 0,
        "pending": 0,
        "in_transit": 0,
        "delivered": 0,
        "total_products": 0,
        "total_stock": 0,
    }
    conn = get_db()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT status, COUNT(*) as cnt FROM shipments GROUP BY status"
            )
            for row in cursor.fetchall():
                stats[row["status"]] = row["cnt"]
                stats["total_shipments"] += row["cnt"]
            cursor.execute(
                "SELECT COUNT(*) as cnt, SUM(quantity) as total FROM inventory"
            )
            inv = cursor.fetchone()
            stats["total_products"] = inv["cnt"] or 0
            stats["total_stock"] = inv["total"] or 0
        finally:
            conn.close()
    return render_template("dashboard.html", stats=stats)


@app.route("/inventory")
def inventory():
    """Inventory list."""
    items = []
    conn = get_db()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM inventory ORDER BY warehouse, product_code")
            items = cursor.fetchall()
        finally:
            conn.close()
    return render_template("inventory.html", items=items)


@app.route("/shipments")
def shipments():
    """Shipments list."""
    items = []
    conn = get_db()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM shipments ORDER BY created_at DESC")
            items = cursor.fetchall()
        finally:
            conn.close()
    return render_template("shipments.html", items=items)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
