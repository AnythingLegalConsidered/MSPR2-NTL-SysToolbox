# Utilitaires — Les fonctions partagées

> Fichiers : `src/utils/network.py`, `src/utils/output.py`, `src/utils/validation.py`
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

### grab_banner(host, port, timeout=3)

Lit la bannière d'un service réseau (SSH, MySQL, etc.). Utile pour identifier un service sans authentification.

```python
from src.utils.network import grab_banner

banner = grab_banner("192.168.10.21", 22)
# → "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6"
```

Retourne la bannière (string) ou `None` si timeout/échec.

### grab_mysql_version(host, port=3306, timeout=3)

Récupère la version MySQL en parsant le paquet de greeting du protocole MySQL. Pas besoin d'authentification.

```python
from src.utils.network import grab_mysql_version

version = grab_mysql_version("192.168.10.21")
# → "8.0.36"
```

Retourne la version (string) ou `None` si pas de MySQL.

### http_check(host, port=80, path="/", timeout=5, verify_ssl=False, scheme=None)

Teste un endpoint HTTP/HTTPS et retourne les métriques de réponse. Auto-détecte HTTPS sur les ports 443, 8443, 4443, 9443.

```python
from src.utils.network import http_check

result = http_check("192.168.10.21", 8006)
# → {"ok": True, "status_code": 200, "server": "pveproxy", "content_length": 1234, "response_time_ms": 45.2, "error": None}
```

Retourne un dict avec : `ok`, `status_code`, `server`, `content_length`, `response_time_ms`, `error`.

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

---

## validation.py — Validation et sanitisation

### sanitize_filename_part(name)

Nettoie une chaîne pour l'utiliser comme partie d'un nom de fichier. Remplace les caractères spéciaux par des underscores, tronque à 50 caractères.

```python
from src.utils.validation import sanitize_filename_part

safe = sanitize_filename_part("check_ad/dns!")
# → "check_ad_dns_"
```

### validate_network_range(target_range)

Valide une plage réseau pour le scan nmap. Accepte : IPv4 simple, notation CIDR, plages nmap (192.168.1.1-50), listes séparées par des virgules.

```python
from src.utils.validation import validate_network_range

err = validate_network_range("192.168.10.0/24")
# → None (valide)

err = validate_network_range("pas-une-ip")
# → "Format de plage réseau invalide: 'pas-une-ip'"
```

Retourne `None` si valide, un message d'erreur (string) si invalide.

### validate_port(port)

Vérifie qu'un numéro de port est dans la plage TCP/UDP valide (1-65535).

```python
from src.utils.validation import validate_port

validate_port(443)   # → True
validate_port(99999) # → False
```

### validate_path_within(path, allowed_dirs)

Empêche les attaques de path traversal en vérifiant qu'un chemin résolu se trouve sous un des répertoires autorisés.

```python
from src.utils.validation import validate_path_within

safe_path = validate_path_within("output/backups/dump.sql", ["./output"])
# → Path résolu

validate_path_within("../../etc/passwd", ["./output"])
# → raises ValueError
```

---

## Tableau récap — Quand utiliser quoi

| Je veux... | Fonction | Fichier |
|------------|----------|---------|
| Vérifier si un port est ouvert | `check_port(host, port)` | `network.py` |
| Pinger une machine | `ping_host(host)` | `network.py` |
| Résoudre un nom DNS | `resolve_dns(hostname, dns_server)` | `network.py` |
| Lire la bannière d'un service | `grab_banner(host, port)` | `network.py` |
| Version MySQL sans auth | `grab_mysql_version(host)` | `network.py` |
| Tester un endpoint HTTP(S) | `http_check(host, port, path)` | `network.py` |
| Afficher un résultat | `print_result(result)` | `output.py` |
| Sauvegarder en JSON | `save_result_json(result)` | `output.py` |
| Configurer les logs | `setup_logging()` | `output.py` |
| Nettoyer un nom de fichier | `sanitize_filename_part(name)` | `validation.py` |
| Valider une plage réseau | `validate_network_range(range)` | `validation.py` |
| Valider un numéro de port | `validate_port(port)` | `validation.py` |
| Vérifier un chemin (anti-traversal) | `validate_path_within(path, dirs)` | `validation.py` |
