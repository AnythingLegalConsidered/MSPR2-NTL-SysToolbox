"""
Module: Backup
Description: Sauvegarde base de donnees MySQL (dump SQL) et export de tables en CSV
Responsable: Ojvind

SOMMAIRE (navigation rapide soutenance) :
─────────────────────────────────────────
- run()                   : Point d'entrée — dispatch vers backup_database ou export_table_csv
- backup_database()       : Sauvegarde une base MySQL via mysqldump (dump .sql horodaté)
- _backup_database_ssh()  : Fallback — exécute mysqldump à distance via SSH (paramiko)
- export_table_csv()      : Exporte une table MySQL en CSV via mysql-connector-python
"""

import csv
import logging
import os
import re
import shlex
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


# --- POINT D'ENTREE DU MODULE BACKUP -----------------------------------------
# Reçoit l'action depuis le menu CLI et dispatch vers la bonne fonction.
# action = "backup_database" → dump SQL | "export_table_csv" → export CSV
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


# --- SAUVEGARDE BASE MYSQL (DUMP SQL) ----------------------------------------
# Exécute mysqldump en local. Si mysqldump n'est pas installé → fallback SSH.
# Le mot de passe est passé via la variable d'env MYSQL_PWD (pas en CLI).
# Le fichier .sql est sauvegardé dans output/backups/ avec un timestamp.
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
    # target may be an IP (from main menu) — use config database name in that case
    database = mysql_cfg.get("database", "wms") if not target or "." in target else target

    # Validate database name to prevent injection in mysqldump CLI args
    if not _VALID_TABLE_RE.match(database):
        raise ModuleConfigError(f"Nom de base invalide: {database!r}")

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
        logger.warning("mysqldump local absent, tentative via SSH...")
        return _backup_database_ssh(config, database, dump_path)
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
# backup_database via SSH (fallback quand mysqldump local absent)
# ---------------------------------------------------------------------------


# --- FALLBACK : DUMP MYSQL VIA SSH (PARAMIKO) --------------------------------
# Si mysqldump n'est pas dispo en local, on se connecte en SSH au serveur MySQL
# et on exécute mysqldump à distance. Le résultat est récupéré via stdout.
# Utilise la lib paramiko (client SSH Python).
def _backup_database_ssh(config: dict, database: str, dump_path: Path) -> dict[str, Any]:
    """Fallback: exécute mysqldump sur le serveur distant via SSH (paramiko)."""
    import paramiko

    ssh_cfg = config.get("ssh", {})
    mysql_cfg = config.get("mysql", {})

    ssh_host = ssh_cfg.get("host", mysql_cfg.get("host", ""))
    ssh_port = ssh_cfg.get("port", 22)
    ssh_user = ssh_cfg.get("user", "")
    ssh_pass = ssh_cfg.get("password", "")

    if not ssh_host or not ssh_user:
        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target=database,
            details={"error": "mysqldump local absent et SSH non configuré"},
            message="mysqldump indisponible localement et SSH non configuré",
        )

    mysql_user = mysql_cfg.get("user", "")
    mysql_pass = mysql_cfg.get("password", "")
    timeout = config.get("general", {}).get("timeout", 10)

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=ssh_host,
            port=ssh_port,
            username=ssh_user,
            password=ssh_pass,
            timeout=timeout,
        )

        # Build remote mysqldump command
        cmd = f"mysqldump --single-transaction --routines -u {mysql_user}"
        if mysql_pass:
            cmd = f"MYSQL_PWD={shlex.quote(mysql_pass)} {cmd}"
        cmd += f" {database}"

        _, stdout, stderr = client.exec_command(cmd, timeout=60)
        exit_code = stdout.channel.recv_exit_status()
        dump_data = stdout.read().decode("utf-8")
        err_data = stderr.read().decode("utf-8").strip()
        client.close()

        if exit_code != 0:
            logger.error("mysqldump SSH échoué: %s", err_data)
            return build_result(
                module=MODULE_NAME,
                function="backup_database",
                status="CRITICAL",
                exit_code=EXIT_CRITICAL,
                target=database,
                details={"error": err_data, "method": "ssh"},
                message=f"mysqldump via SSH échoué: {err_data}",
            )

        dump_path.parent.mkdir(parents=True, exist_ok=True)
        dump_path.write_text(dump_data, encoding="utf-8")
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
                "method": "ssh",
            },
            message=f"Backup {database} via SSH: {dump_path} ({size_bytes} octets)",
        )

    except Exception as e:
        logger.error("backup_database SSH failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="backup_database",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target=database,
            details={"error": str(e), "method": "ssh"},
            message=f"Erreur backup SSH: {e}",
        )


# ---------------------------------------------------------------------------
# export_table_csv
# ---------------------------------------------------------------------------


# --- EXPORT TABLE MYSQL → CSV ------------------------------------------------
# Se connecte à MySQL via mysql-connector-python, fait un SELECT * sur la table,
# puis écrit les résultats en CSV horodaté dans output/exports/.
# Le nom de table est validé par regex pour éviter l'injection SQL.
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
            # Safety check: _VALID_TABLE_RE validated at function entry
            if not _VALID_TABLE_RE.match(target):
                raise ModuleConfigError(f"Table name validation bypass: {target!r}")
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
