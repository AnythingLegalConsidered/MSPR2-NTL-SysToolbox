#!/usr/bin/env python3

import argparse
import json
import sys
from datetime import datetime

from checks import check_dns, check_ports, check_ldap, check_services
from constants import EXIT_CODES


def evaluate(statuses):
    if "CRITICAL" in statuses:
        return "CRITICAL"
    if "WARNING" in statuses:
        return "WARNING"
    if "UNKNOWN" in statuses:
        return "UNKNOWN"
    return "OK"


def main():
    parser = argparse.ArgumentParser(description="AD/DNS Health Check")

    parser.add_argument("--host", required=True)
    parser.add_argument("--dns")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    timestamp = datetime.utcnow().isoformat() + "Z"

    # Checks
    dns_ok, dns_info = check_dns(args.host, args.dns)
    port_status, ports = check_ports(args.host)
    ldap_ok = check_ldap(args.host)

    if args.username and args.password:
        svc_status, services = check_services(
            args.host,
            args.username,
            args.password
        )
    else:
        svc_status = "UNKNOWN"
        services = "Not checked"

    statuses = [
        "OK" if dns_ok else "CRITICAL",
        port_status,
        svc_status,
        "OK" if ldap_ok else "CRITICAL"
    ]

    overall = evaluate(statuses)

    output = {
        "timestamp": timestamp,
        "host": args.host,
        "dns_server_used": args.dns or "system_default",
        "results": {
            "dns": dns_info,
            "ports": ports,
            "ldap": ldap_ok,
            "services": services
        },
        "overall_status": overall
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n=== AD/DNS Check: {args.host} ===")
        print(f"DNS: {'OK' if dns_ok else 'FAILED'} ({dns_info})")
        print(f"Ports: {port_status}")
        print(f"LDAP: {'OK' if ldap_ok else 'FAILED'}")
        print(f"Services: {svc_status}")
        print(f"\nGLOBAL STATUS: {overall}")

    sys.exit(EXIT_CODES[overall])


if __name__ == "__main__":
    main()