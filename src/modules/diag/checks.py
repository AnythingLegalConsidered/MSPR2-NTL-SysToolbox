import socket
import dns.resolver
from ldap3 import Server, Connection, ALL
import winrm
from constants import CRITICAL_PORTS, IMPORTANT_PORTS, SERVICES


# DNS
def check_dns(host, dns_server=None, timeout=3):
    try:
        if dns_server:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.timeout = timeout
            resolver.lifetime = timeout
            answers = resolver.resolve(host, "A")
            return True, answers[0].to_text()
        else:
            socket.setdefaulttimeout(timeout)
            return True, socket.gethostbyname(host)
    except Exception as e:
        return False, str(e)


# Ports
def check_ports(host, timeout=2):
    results = {}
    overall = "OK"

    for port in CRITICAL_PORTS + IMPORTANT_PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        try:
            sock.connect((host, port))
            results[port] = True
        except Exception:
            results[port] = False
            if port in CRITICAL_PORTS:
                overall = "CRITICAL"
            elif overall != "CRITICAL":
                overall = "WARNING"
        finally:
            sock.close()

    return overall, results


# LDAP
def check_ldap(host):
    try:
        server = Server(host, get_info=ALL)
        conn = Connection(server, auto_bind=True)
        conn.unbind()
        return True
    except Exception:
        return False


# WinRM Services
def check_services(host, username, password):
    results = {}
    overall = "OK"

    try:
        session = winrm.Session(host, auth=(username, password))

        for service in SERVICES:
            ps = f"Get-Service -Name {service} | Select-Object -ExpandProperty Status"
            r = session.run_ps(ps)

            if r.status_code == 0:
                status = r.std_out.decode().strip()
                results[service] = status
                if status != "Running":
                    overall = "CRITICAL"
            else:
                results[service] = "Error"
                overall = "CRITICAL"

    except Exception as e:
        return "UNKNOWN", {"error": str(e)}

    return overall, results