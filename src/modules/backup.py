"""
Module: [backup]
Description: WMS database backup and CSV export module
Responsible: ojvind
"""

import csv
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.interfaces import (
    EXIT_CRITICAL,
    EXIT_OK,
    EXIT_UNKNOWN,
    ModuleConfigError,
    ModuleExecutionError,
    build_result,
)

logger = logging.getLogger(__name__)

MODULE_NAME = "[backup]"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(config: dict, target: str, **kwargs: Any) -> dict[str, Any]:
    """Main entry point for the backup module.

    Dispatches to backup_database() or export_table_csv() based on action.

    Args:
        config: Full config dict loaded from config.yaml.
        target: Database name for backup, or table name for CSV export.
        **kwargs: Must include action="backup_database" or action="export_table_csv".

    Raises:
        ModuleConfigError: If action is unknown or table_name is missing.
        ModuleExecutionError: If execution fails unexpectedly.
    """
    logger.info("Starting %s on target: %s", MODULE_NAME, target)

    action = kwargs.get("action", "backup_database")

    try:
        if action == "backup_database":
            db_name = target or config.get("mysql", {}).get("database", "wms")
            return backup_database(config, db_name)

        elif action == "export_table_csv":
            table_name = kwargs.get("table_name") or target
            if not table_name:
                raise ModuleConfigError("export_table_csv requires a table name (target or table_name kwarg)")
            return export_table_csv(config, table_name)

        else:
            raise ModuleConfigError(f"Unknown action: {action}")

    except ModuleConfigError:
        raise
    except Exception as e:
        logger.error("%s execution failed: %s", MODULE_NAME, e)
        raise ModuleExecutionError(str(e)) from e


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _sha256(file_path: Path) -> str:
    """Compute SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# backup_database — Issue #8
# ---------------------------------------------------------------------------

def backup_database(config: dict, db_name: str) -> dict[str, Any]:
    """Create a full MySQL dump via SSH and save it locally with SHA256.

    Connects to the remote WMS-DB server via SSH (paramiko), executes
    mysqldump, and writes the output to output/backups/<db>_YYYYMMDD_HHMMSS.sql.

    Args:
        config: Config dict with ssh and mysql sections.
        db_name: Name of the database to dump.

    Returns:
        Standardized result dict.
    """
    try:
        import paramiko  # type: ignore[import]
    except ImportError:
        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=db_name,
            details={"error": "paramiko not installed. Run: pip install paramiko"},
            message="paramiko is required for SSH-based backup",
        )

    ssh_conf = config.get("ssh", {})
    mysql_conf = config.get("mysql", {})
    output_dir = config.get("general", {}).get("output_dir", "./output")

    host = ssh_conf.get("host", "")
    port = int(ssh_conf.get("port", 22))
    user = ssh_conf.get("user", "")
    password = ssh_conf.get("password", "")
    key_file = ssh_conf.get("key_file")
    mysql_user = mysql_conf.get("user", "")
    mysql_pass = mysql_conf.get("password", "")

    if not host or not user:
        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=db_name,
            details={"error": "SSH host or user not configured"},
            message="Missing SSH configuration",
        )

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        connect_kwargs: dict[str, Any] = {"hostname": host, "port": port, "username": user}
        if key_file:
            connect_kwargs["key_filename"] = key_file
        else:
            connect_kwargs["password"] = password

        client.connect(**connect_kwargs)
        logger.info("SSH connected to %s", host)

        # Build mysqldump command (password via env to avoid shell history)
        dump_cmd = (
            f"MYSQL_PWD='{mysql_pass}' mysqldump -u {mysql_user} --databases {db_name}"
        )
        _, stdout, stderr = client.exec_command(dump_cmd)
        dump_data = stdout.read()
        err = stderr.read().decode("utf-8", errors="replace").strip()

        if not dump_data:
            logger.error("mysqldump produced no output: %s", err)
            return build_result(
                module=MODULE_NAME,
                function="backup_database",
                status="CRITICAL",
                exit_code=EXIT_CRITICAL,
                target=db_name,
                details={"error": err or "Empty dump output"},
                message=f"Backup failed for {db_name}: no data received",
            )

        # Count tables from the dump (rough estimate via CREATE TABLE lines)
        table_count = dump_data.count(b"CREATE TABLE")

        # Save locally
        backup_dir = Path(output_dir) / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        sql_path = backup_dir / f"{db_name}_{ts}.sql"

        sql_path.write_bytes(dump_data)
        checksum = _sha256(sql_path)
        size_bytes = sql_path.stat().st_size

        logger.info("Backup saved to %s (%d bytes)", sql_path, size_bytes)

        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="OK",
            exit_code=EXIT_OK,
            target=db_name,
            details={
                "file": str(sql_path),
                "size_bytes": size_bytes,
                "sha256": checksum,
                "table_count": table_count,
            },
            message=f"Backup OK: {db_name} → {sql_path.name} ({size_bytes} bytes, {table_count} tables)",
        )

    except Exception as e:
        logger.error("backup_database failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target=db_name,
            details={"error": str(e)},
            message=f"Backup failed: {e}",
        )

    finally:
        client.close()


# ---------------------------------------------------------------------------
# export_table_csv — Issue #9
# ---------------------------------------------------------------------------

def export_table_csv(config: dict, table_name: str) -> dict[str, Any]:
    """Export a MySQL table to a CSV file with SHA256.

    Connects directly to MySQL, executes SELECT * FROM <table_name>,
    and writes results to output/backups/<table>_YYYYMMDD_HHMMSS.csv.

    Args:
        config: Config dict with mysql section.
        table_name: Name of the table to export.

    Returns:
        Standardized result dict.
    """
    try:
        import mysql.connector  # type: ignore[import]
    except ImportError:
        return build_result(
            module=MODULE_NAME,
            function="export_table_csv",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=table_name,
            details={"error": "mysql-connector-python not installed. Run: pip install mysql-connector-python"},
            message="mysql-connector-python is required for CSV export",
        )

    mysql_conf = config.get("mysql", {})
    output_dir = config.get("general", {}).get("output_dir", "./output")

    host = mysql_conf.get("host", "")
    port = int(mysql_conf.get("port", 3306))
    user = mysql_conf.get("user", "")
    password = mysql_conf.get("password", "")
    database = mysql_conf.get("database", "")

    if not host or not user or not database:
        return build_result(
            module=MODULE_NAME,
            function="export_table_csv",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=table_name,
            details={"error": "MySQL host, user or database not configured"},
            message="Missing MySQL configuration",
        )

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        cursor = conn.cursor()
        logger.info("MySQL connected to %s/%s", host, database)

        cursor.execute(f"SELECT * FROM `{table_name}`")  # noqa: S608
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Save CSV
        backup_dir = Path(output_dir) / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = backup_dir / f"{table_name}_{ts}.csv"

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)

        checksum = _sha256(csv_path)
        size_bytes = csv_path.stat().st_size
        row_count = len(rows)

        logger.info("CSV export saved to %s (%d rows)", csv_path, row_count)

        return build_result(
            module=MODULE_NAME,
            function="export_table_csv",
            status="OK",
            exit_code=EXIT_OK,
            target=table_name,
            details={
                "file": str(csv_path),
                "columns": columns,
                "row_count": row_count,
                "size_bytes": size_bytes,
                "sha256": checksum,
            },
            message=f"Export OK: {table_name} → {csv_path.name} ({row_count} rows)",
        )

    except Exception as e:
        logger.error("export_table_csv failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="export_table_csv",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target=table_name,
            details={"error": str(e)},
            message=f"CSV export failed: {e}",
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
