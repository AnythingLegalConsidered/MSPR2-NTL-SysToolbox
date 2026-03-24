"""
Module: Backup
Description: Sauvegarde base de donnees MySQL (dump SQL) et export de tables en CSV
Responsable: Ojvind
"""

import csv
import logging
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from src.interfaces import (
    EXIT_CRITICAL,
    EXIT_OK,
    EXIT_UNKNOWN,
    ModuleConfigError,
    build_result,
)
from src.utils.validation import validate_path_within

logger = logging.getLogger(__name__)

MODULE_NAME = "backup"

# Regex for valid SQL table names (letters, digits, underscores, max 64 chars)
_VALID_TABLE_RE = re.compile(r"^[a-zA-Z_]\w{0,63}$")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run(config: dict, target: str, **kwargs: Any) -> dict[str, Any]:
    """Point d'entree principal du module backup.

    Args:
        config: Config complete chargee depuis config.yaml.
        target: Nom de la base ou de la table selon l'action.
        **kwargs: action = "backup_database" | "export_table_csv"
    """
    action = kwargs.get("action", "")
    logger.info("Backup action=%s sur cible: %s", action, target)

    if action == "backup_database":
        return backup_database(config, target)
    elif action == "export_table_csv":
        return export_table_csv(config, target)
    else:
        return build_result(
            module=MODULE_NAME,
            function=action or "run",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={},
            message=f"Action '{action}' non reconnue.",
        )


# ---------------------------------------------------------------------------
# backup_database
# ---------------------------------------------------------------------------


def backup_database(config: dict, target: str) -> dict[str, Any]:
    """Sauvegarde une base MySQL via mysqldump.

    Args:
        config: Config complete (utilise mysql.* et general.*).
        target: Nom de la base a sauvegarder (ex: wms).

    Returns:
        Resultat standardise via build_result().

    Raises:
        ModuleConfigError: Si la section 'mysql' est absente du config.
    """
    mysql_cfg = config.get("mysql", {})
    if not mysql_cfg:
        raise ModuleConfigError("Section 'mysql' manquante dans config.yaml")

    timeout = config.get("general", {}).get("timeout", 10)
    output_dir = config.get("general", {}).get("output_dir", "./output")
    try:
        validate_path_within(output_dir, [os.getcwd(), os.path.realpath(output_dir)])
    except ValueError as exc:
        raise ModuleConfigError(str(exc)) from exc

    host = mysql_cfg.get("host", "127.0.0.1")
    port = str(mysql_cfg.get("port", 3306))
    user = mysql_cfg.get("user", "")
    password = mysql_cfg.get("password", "")
    database = target or mysql_cfg.get("database", "wms")

    backup_dir = Path(output_dir) / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_path = backup_dir / f"{database}_{ts}.sql"

    try:
        cmd = [
            "mysqldump",
            f"--host={host}",
            f"--port={port}",
            f"--user={user}",
            "--single-transaction",
            "--routines",
            database,
        ]

        # SECURITY NOTE: MYSQL_PWD via env var is visible in /proc/PID/environ on Linux.
        # However, this is the recommended approach per MySQL documentation:
        # - --password on CLI is visible in `ps aux` (worse)
        # - MYSQL_PWD env var is the least-bad option for automated tools.
        env = os.environ.copy()
        if password:
            env["MYSQL_PWD"] = password

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip()

            if "access denied" in error_msg.lower():
                return build_result(
                    module=MODULE_NAME,
                    function="backup_database",
                    status="CRITICAL",
                    exit_code=EXIT_CRITICAL,
                    target=database,
                    details={"error": error_msg},
                    message=f"Acces refuse a la base {database}",
                )

            return build_result(
                module=MODULE_NAME,
                function="backup_database",
                status="CRITICAL",
                exit_code=EXIT_CRITICAL,
                target=database,
                details={"error": error_msg},
                message=f"mysqldump echoue: {error_msg}",
            )

        dump_path.write_text(result.stdout, encoding="utf-8")
        size_bytes = dump_path.stat().st_size

        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="OK",
            exit_code=EXIT_OK,
            target=database,
            details={
                "dump_path": str(dump_path),
                "size_bytes": size_bytes,
                "database": database,
            },
            message=f"Backup {database} sauvegarde: {dump_path} ({size_bytes} octets)",
        )

    except FileNotFoundError:
        logger.error("mysqldump non disponible sur ce systeme")
        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target=database,
            details={"error": "mysqldump non disponible"},
            message="mysqldump non disponible — installez mysql-client",
        )
    except subprocess.TimeoutExpired:
        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=database,
            details={"error": "Timeout mysqldump"},
            message=f"Timeout lors du dump de {database}",
        )
    except Exception as e:
        logger.error("backup_database failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target=database,
            details={"error": str(e)},
            message=f"Erreur lors du backup: {e}",
        )


# ---------------------------------------------------------------------------
# export_table_csv
# ---------------------------------------------------------------------------


def export_table_csv(config: dict, target: str) -> dict[str, Any]:
    """Exporte une table MySQL en fichier CSV.

    Args:
        config: Config complete (utilise mysql.* et general.*).
        target: Nom de la table a exporter (ex: shipments).

    Returns:
        Resultat standardise via build_result().

    Raises:
        ModuleConfigError: Si la section 'mysql' est absente du config.
    """
    mysql_cfg = config.get("mysql", {})
    if not mysql_cfg:
        raise ModuleConfigError("Section 'mysql' manquante dans config.yaml")

    if not target:
        raise ModuleConfigError("Nom de table requis pour l'export CSV")

    if not _VALID_TABLE_RE.match(target):
        raise ModuleConfigError(f"Nom de table invalide: {target!r}")

    timeout = config.get("general", {}).get("timeout", 10)
    output_dir = config.get("general", {}).get("output_dir", "./output")
    try:
        validate_path_within(output_dir, [os.getcwd(), os.path.realpath(output_dir)])
    except ValueError as exc:
        raise ModuleConfigError(str(exc)) from exc

    database = mysql_cfg.get("database", "wms")

    export_dir = Path(output_dir) / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = export_dir / f"{target}_{ts}.csv"

    try:
        import mysql.connector  # type: ignore[import]

        conn = mysql.connector.connect(
            host=mysql_cfg.get("host", "127.0.0.1"),
            port=mysql_cfg.get("port", 3306),
            user=mysql_cfg.get("user", ""),
            password=mysql_cfg.get("password", ""),
            database=database,
            connection_timeout=timeout,
        )
        try:
            cursor = conn.cursor()
            # Safety assertion: _VALID_TABLE_RE validated at function entry
            assert _VALID_TABLE_RE.match(target), f"Table name validation bypass: {target!r}"
            cursor.execute(f"SELECT * FROM `{target}`")  # noqa: S608
            columns = [desc[0] for desc in cursor.description]  # type: ignore[union-attr]
            rows = cursor.fetchall()
            cursor.close()
        finally:
            conn.close()

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)

        return build_result(
            module=MODULE_NAME,
            function="export_table_csv",
            status="OK",
            exit_code=EXIT_OK,
            target=target,
            details={
                "csv_path": str(csv_path),
                "table": target,
                "database": database,
                "row_count": len(rows),
                "columns": columns,
            },
            message=f"Export {target}: {len(rows)} lignes -> {csv_path}",
        )

    except Exception as e:
        err = str(e).lower()
        if "access denied" in err or "authentication" in err:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"Acces refuse a la base {database}"
        elif "doesn't exist" in err or "not exist" in err:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"Table '{target}' introuvable dans {database}"
        elif any(kw in err for kw in ("can't connect", "connection refused", "timed out")):
            status, code = "UNKNOWN", EXIT_UNKNOWN
            msg = f"Serveur MySQL injoignable: {e}"
        else:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"Erreur export CSV: {e}"

        logger.error("export_table_csv failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="export_table_csv",
            status=status,
            exit_code=code,
            target=target,
            details={"error": str(e), "table": target, "database": database},
            message=msg,
        )
