# Utilitaires — Les fonctions partagées

> Fichiers : `src/utils/network.py`, `src/utils/output.py`
> Rôle : Fonctions réutilisables par tous les modules. Pas besoin de réinventer la roue.

## network.py — Outils réseau

### check_port(host, port, timeout=10)

Vérifie si un port TCP est ouvert sur une machine.

```python
from src.utils.network import check_port

if check_port("192.168.10.10", 389):   # Port LDAP
    print("LDAP accessible")
else:
    print("LDAP down")
```

Retourne `True` (ouvert) ou `False` (fermé/timeout).

### ping_host(host, timeout=10)

Ping ICMP classique. Fonctionne sur Windows et Linux automatiquement.

```python
from src.utils.network import ping_host

if ping_host("192.168.10.10"):
    print("Machine joignable")
```

Retourne `True` (répond) ou `False` (timeout).

### resolve_dns(hostname, dns_server=None)

Résout un nom de domaine en IP.

```python
from src.utils.network import resolve_dns

# Résolution standard (DNS système)
ip = resolve_dns("ntl.local")

# Résolution via un serveur DNS spécifique (DC01)
ip = resolve_dns("ntl.local", dns_server="192.168.10.10")
```

Retourne l'IP (string) ou `None` si échec.

---

## output.py — Affichage et logs

### setup_logging(log_level, output_dir)

Configure les logs pour toute l'app. **Appelé une seule fois** au démarrage par `main.py`.

```python
setup_logging(log_level="INFO", output_dir="./output")
```

Format des logs : `2026-02-26 14:30:00 [INFO] src.modules.diagnostic — Message`

### print_result(result)

Affiche un résultat JSON formaté dans le terminal (avec couleurs via `rich` si installé).

```python
from src.utils.output import print_result

print_result(result)  # result = ce que build_result() retourne
```

### save_result_json(result, output_dir)

Sauvegarde le résultat en fichier JSON horodaté.

```python
from src.utils.output import save_result_json

path = save_result_json(result, output_dir="./output")
# → output/logs/20260226_143000_diagnostic_check_ad_dns.json
```

---

## Tableau récap — Quand utiliser quoi

| Je veux... | Fonction | Fichier |
|------------|----------|---------|
| Vérifier si un port est ouvert | `check_port(host, port)` | `network.py` |
| Pinger une machine | `ping_host(host)` | `network.py` |
| Résoudre un nom DNS | `resolve_dns(hostname)` | `network.py` |
| Afficher un résultat | `print_result(result)` | `output.py` |
| Sauvegarder en JSON | `save_result_json(result)` | `output.py` |
| Configurer les logs | `setup_logging()` | `output.py` |
