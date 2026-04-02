# Logique des modules — Implementation

> Ce document contient deux parties :
> 1. **Comment implementer un module** (patron a suivre)
> 2. **Logique detaillee** de chaque fonction, module par module

---

## Comment implementer un module

> Template : `src/modules/_template.py`

### Etape 1 — Copier le template

```bash
cp src/modules/_template.py src/modules/diagnostic.py
```

### Etape 2 — Renommer les placeholders

En haut du fichier, change :

```python
MODULE_NAME = "diagnostic"  # etait "[NOM DU MODULE]"
```

### Etape 3 — Implementer la fonction run()

C'est le point d'entree. `main.py` appelle toujours `run()`.

```python
def run(config: dict, target: str, **kwargs) -> dict:
    action = kwargs.get("action", "")

    if action == "check_ad_dns":
        return check_ad_dns(config, target)
    elif action == "check_mysql":
        return check_mysql(config, target)
    else:
        raise ModuleExecutionError(f"Action inconnue: {action}")
```

**Parametres recus :**
- `config` → tout le config.yaml (deja resolu, secrets inclus)
- `target` → l'IP ou nom saisi par l'utilisateur
- `action` → quelle fonction appeler (passe par main.py)

### Etape 4 — Implementer les fonctions

**Les 2 regles d'or :**
1. **Toujours** retourner `build_result()`
2. **Toujours** attraper les exceptions (jamais de crash)

**Exemple concret : check_mysql (version simplifiee)**

```python
def _check_mysql(config: dict, target: str) -> dict:
    try:
        port = config.get("mysql", {}).get("port", 3306)
        result = check_mysql_port(target, port)

        if result["reachable"]:
            status, code = "OK", EXIT_OK
            msg = f"MySQL accessible sur {target}:{port}"
        else:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"MySQL injoignable sur {target}:{port}"

        return build_result(
            module=MODULE_NAME,
            function="check_mysql",
            status=status,
            exit_code=code,
            target=target,
            details=result,
            message=msg,
        )

    except Exception as exc:
        logger.error("check_mysql failed: %s", exc)
        return build_result(
            module=MODULE_NAME,
            function="check_mysql",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(exc)},
            message=f"Erreur lors du check MySQL sur {target}: {exc}",
        )
```

### Checklist avant de push

- [ ] `MODULE_NAME` est correct
- [ ] `run()` dispatch vers les bonnes fonctions
- [ ] Chaque fonction retourne `build_result()`
- [ ] Chaque fonction a un try/except (pas de crash possible)
- [ ] Les imports sont en haut du fichier
- [ ] `ruff` et `mypy` passent (`make lint && make typecheck`)

---

# Logique detaillee par module

> Ce qui suit explique ce que fait chaque module, fonction par fonction.
> Pas de code ici — juste la logique, les entrees, les sorties et le raisonnement.

---

## Module 1 — Diagnostic

**Dossier :** `src/modules/diagnostic/` (`__init__.py`, `checks.py`, `constant.py`)
**Responsable :** Blaise
**But :** Verifier que les services critiques de NTL fonctionnent.

### 1.1 check_ad_dns()

**Cible :** DC01 (192.168.10.10)
**Question :** "Est-ce que l'Active Directory et le DNS tournent ?"

**Logique :**

```
1. Resoudre le domaine AD (config: discovery.domain, defaut "ntl.local")
   via le DNS de la cible (dnspython)
   → Ca resout ? Le DNS fonctionne.
   → Ca ne resout pas ? DNS KO.

2. Tester les ports critiques et importants du DC :
   → Critiques : 53 (DNS), 88 (Kerberos), 389 (LDAP)
   → Importants : 445 (SMB), 3268 (LDAP-GC)
   → Un port critique ferme = CRITICAL
   → Un port important ferme = WARNING

3. Tester la connectivite LDAP (via ldap3, connexion reelle)
   → Bind OK ? LDAP fonctionnel.
   → Bind KO ? LDAP down.

4. (Optionnel) Verifier les services Windows via WinRM :
   → Necessite config winrm.user + winrm.password
   → Services verifies : NTDS, DNS, Netlogon
   → Si WinRM non configure → SKIPPED (n'impacte pas le status)

5. Decider du status global :
   ┌────────────────────────────────────────┬──────────┐
   │ DNS + ports + LDAP OK                  │ OK       │
   │ Un check CRITICAL (DNS/port/LDAP)      │ CRITICAL │
   │ Un check UNKNOWN (ex: WinRM erreur)    │ WARNING  │
   │ Exception inattendue                   │ UNKNOWN  │
   └────────────────────────────────────────┴──────────┘
```

**Utilise :** `check_dns()`, `check_ports()`, `check_ldap()` (ldap3), `check_services()` (pywinrm, optionnel)
**Details retournes :** `dns: {ok, info}`, `ports: {status, results}`, `ldap: {ok}`, `services: {status, results}`

---

### 1.2 check_mysql()

**Cible :** WMS-DB (192.168.10.21)
**Question :** "Est-ce que MySQL repond ?"

**Logique :**

```
1. Tester le port MySQL (config: mysql.port, defaut 3306)
   → Port ouvert ? Continuer.
   → Port ferme ? Status CRITICAL.

2. Recuperer la version MySQL sans authentification :
   → Parser le paquet de greeting du protocole MySQL
   → Si le greeting ne contient pas de version → tenter grab_banner()

3. Decider du status :
   ┌──────────────────────────────────────────┬──────────┐
   │ Port ouvert (+ version detectee)         │ OK       │
   │ Port ferme                               │ CRITICAL │
   │ Exception inattendue                     │ UNKNOWN  │
   └──────────────────────────────────────────┴──────────┘
```

**Note :** Ce check est non-authentifie — il verifie uniquement que le service MySQL ecoute et repond. Pas de SHOW DATABASES ni SHOW STATUS.

**Utilise :** `check_mysql_port()` → `check_port()`, `grab_mysql_version()`, `grab_banner()`
**Details retournes :** `reachable: true/false`, `port: N`, `version: "8.0.36" ou null`, `banner: "..." ou null`

---

### 1.3 check_linux()

**Cible :** Tout serveur Linux (ex: WMS-DB)
**Question :** "Quels services tournent sur ce serveur ?"

**Logique :**

```
1. Lire la liste de ports a scanner :
   → Config : discovery.ports (liste personnalisable)
   → Defaut (DISCOVERY_PORTS) : 22, 80, 443, 3306, 5432, 8006, 8080
   → Timeout par port : discovery.timeout (defaut 2s)

2. Pour chaque port, tester avec check_port() :
   → Port ouvert ? Identifier le service (via SERVICE_NAMES de constant.py)
   → SERVICE_NAMES mappe : 22→SSH, 80→HTTP, 443→HTTPS, 3306→MySQL, etc.

3. Collecter les categories de services trouves (set unique, trie)

4. Decider du status :
   ┌──────────────────────────────────────┬──────────┐
   │ Au moins un service trouve           │ OK       │
   │ Aucun service detecte                │ CRITICAL │
   │ Exception inattendue                 │ UNKNOWN  │
   └──────────────────────────────────────┴──────────┘
```

**Utilise :** `check_host_services()` → `check_port()` (network.py), `DISCOVERY_PORTS`/`SERVICE_NAMES` (constant.py)
**Details retournes :** `host: "..."`, `open_ports: [{port, service, open}]`, `categories: ["SSH", "MySQL", ...]`

---

### 1.4 check_http()

**Cible :** Tout serveur HTTP/HTTPS
**Question :** "Est-ce que le service web repond correctement ?"

**Logique :**

```
1. Parser la cible :
   → Si format "host:port" → extraire le port
   → Sinon → port 80 par defaut

2. Envoyer une requete HTTP(S) via http_check() :
   → Auto-detection HTTPS sur ports 443, 8443, 4443, 9443
   → Verification SSL desactivee (environnement lab)
   → User-Agent : "NTL-SysToolbox/1.0"

3. Recuperer les metriques :
   → Code HTTP (200, 301, 404...)
   → Header "Server"
   → Taille du contenu
   → Temps de reponse (ms)

4. Decider du status :
   ┌────────────────────────────────────┬──────────┐
   │ Reponse HTTP recue (ok=true)       │ OK       │
   │ Erreur HTTP ou connexion refusee   │ CRITICAL │
   │ Exception inattendue               │ UNKNOWN  │
   └────────────────────────────────────┴──────────┘
```

**Utilise :** `check_http()` (checks.py) → `http_check()` (network.py)
**Details retournes :** `ok: true/false`, `status_code: N`, `server: "..."`, `content_length: N`, `response_time_ms: N`, `error: "..." ou null`

---

## Module 2 — Backup

**Fichier :** `src/modules/backup.py`
**Responsable :** Ojvind
**But :** Sauvegarder la base WMS et exporter des tables en CSV.

### 2.1 backup_database()

**Cible :** Base `wms` sur WMS-DB
**Question :** "Faire un dump complet de la base et verifier son integrite."

**Logique :**

```
1. Se connecter en SSH a WMS-DB

2. Executer mysqldump via SSH :
   → mysqldump -u wms_user -p wms > dump.sql
   → Resultat recupere en local

3. Sauvegarder le fichier :
   → Nom : wms_20260226_143000.sql
   → Dossier : output/backups/

4. Verifier l'integrite :
   → Calculer le hash SHA256 du fichier
   → Verifier que la taille > 0 octets

5. Decider du status :
   ┌────────────────────────────────────────┬──────────┐
   │ Fichier cree + taille > 0 + SHA256    │ OK       │
   │ Fichier vide                          │ CRITICAL │
   │ mysqldump echoue                      │ CRITICAL │
   │ SSH echoue                            │ UNKNOWN  │
   └────────────────────────────────────────┴──────────┘
```

**Utilise :** `paramiko` (SSH), `subprocess` (mysqldump), `hashlib` (SHA256)
**Details retournes :** `file_path: "..."`, `file_size_bytes: N`, `sha256: "abc123..."`, `duration_seconds: N`

---

### 2.2 export_table_csv()

**Cible :** Une table de la base `wms` (ex: `shipments`, `inventory`)
**Question :** "Exporter le contenu d'une table en fichier CSV."

**Logique :**

```
1. Se connecter a MySQL avec mysql-connector-python

2. Executer : SELECT * FROM <table>

3. Ecrire le resultat en CSV :
   → Nom : shipments_20260226_143000.csv
   → Dossier : output/backups/
   → Encodage : UTF-8
   → Separateur : virgule (,)
   → Premiere ligne = noms des colonnes

4. Calculer le SHA256

5. Decider du status :
   ┌─────────────────────────────┬──────────┐
   │ Fichier cree + donnees OK   │ OK       │
   │ Table vide (0 lignes)       │ WARNING  │
   │ Table inexistante           │ CRITICAL │
   │ Connexion MySQL echoue      │ UNKNOWN  │
   └─────────────────────────────┴──────────┘
```

**Utilise :** `mysql-connector-python` (SELECT), `csv` (ecriture), `hashlib` (SHA256)
**Details retournes :** `file_path: "..."`, `row_count: N`, `columns: [...]`, `sha256: "..."`, `table: "shipments"`

---

## Module 3 — Audit

**Dossier :** `src/modules/audit/` (`__init__.py`, `scanner.py`)
**Responsable :** Zaid
**But :** Scanner le reseau, identifier les OS obsoletes, generer un rapport.

### 3.1 scan_network()

**Cible :** Plage reseau (ex: 192.168.10.0/24)
**Question :** "Quelles machines sont sur le reseau et quels services tournent ?"

**Logique :**

```
1. Detecter si on a les droits admin
   → Admin : scan complet (nmap -sV -O)
   → Pas admin : scan degrade (nmap -sT -sV) + WARNING

2. Scanner la plage reseau avec python-nmap

3. Pour chaque machine trouvee, recuperer :
   → IP
   → Hostname (si detectable)
   → OS detecte (si droits admin)
   → Ports ouverts + services

4. Decider du status :
   ┌──────────────────────────────────┬──────────┐
   │ Scan termine, machines trouvees  │ OK       │
   │ Scan degrade (pas admin)         │ WARNING  │
   │ nmap pas installe                │ CRITICAL │
   │ Reseau injoignable               │ UNKNOWN  │
   └──────────────────────────────────┴──────────┘
```

**Utilise :** `python-nmap` (scan reseau)
**Details retournes :** `hosts_found: N`, `hosts: [{ip, hostname, os, ports: [...]}]`, `scan_type: "full/degraded"`

---

### 3.2 list_os_eol()

**Cible :** Tous les OS de la base EOL locale
**Question :** "Quelles sont les dates de fin de vie de chaque OS ?"

**Logique :**

```
1. Lire le fichier data/eol_database.json

2. Pour chaque OS, calculer :
   → Jours restants avant EOL
   → Status : EXPIRE / BIENTOT (< 6 mois) / OK

3. Trier par urgence : EXPIRE en premier, puis BIENTOT, puis OK

4. Status toujours OK (c'est juste une consultation de donnees)
```

**Source de donnees :** `data/eol_database.json` — fichier local, pas d'appel reseau
**Details retournes :** `os_list: [{name, eol_date, days_remaining, status: "expired/soon/ok"}]`

---

### 3.3 audit_from_csv()

**Cible :** Fichier CSV d'inventaire (ex: `data/sample_inventory.csv`)
**Question :** "Quelles machines de notre parc ont un OS obsolete ?"

**Logique :**

```
1. Lire le CSV d'inventaire (hostname, os_name, os_version, role)

2. Pour chaque ligne du CSV :
   → Reconstituer le nom complet de l'OS (ex: "Windows Server" + "2022" → "Windows Server 2022")
   → Chercher dans eol_database.json
   → Calculer les jours restants

3. Classer chaque machine :
   ┌──────────────────────────────────────┬──────────┐
   │ EOL depassee                         │ EXPIRE   │
   │ EOL dans moins de 6 mois            │ BIENTOT  │
   │ EOL dans plus de 6 mois             │ OK       │
   │ OS pas trouve dans la base EOL      │ INCONNU  │
   └──────────────────────────────────────┴──────────┘

4. Exemple avec l'inventaire NTL :
   SRV-PRINT (Win Server 2008 R2) → EXPIRE (depuis 2023)
   PC-QUAI-WH1 (Windows 7)        → EXPIRE (depuis 2023)
   SRV-FILE (Win Server 2012 R2)  → BIENTOT (oct 2026)
   DC01 (Win Server 2022)          → OK (jusqu'en 2031)
```

**Utilise :** `csv` (lecture), `json` (base EOL), `datetime` (calcul des jours)
**Details retournes :** `total_hosts: N`, `expired: N`, `soon: N`, `ok: N`, `unknown: N`, `hosts: [...]`

---

### 3.4 generate_report()

**Cible :** Resultat combine de scan_network + audit_from_csv
**Question :** "Generer un rapport complet d'obsolescence, trie par criticite."

**Logique :**

```
1. Lancer audit_from_csv() (ou utiliser les resultats deja en memoire)

2. Trier les resultats par criticite :
   → D'abord les EXPIRE (rouge)
   → Puis les BIENTOT (orange)
   → Puis les OK (vert)

3. Generer 2 sorties :
   → Tableau rich dans le terminal (colore, lisible)
   → Fichier JSON dans output/reports/

4. Le rapport contient pour chaque machine :
   → Hostname
   → OS actuel
   → Date EOL
   → Jours restants (ou "expire depuis X jours")
   → Role dans l'infra
   → Recommandation (mettre a jour vers quelle version)
```

**Utilise :** `rich` (affichage colore), `json` (export)
**Details retournes :** `report_path: "..."`, `summary: {expired: N, soon: N, ok: N}`, `generated_at: "..."`

---

## Resume visuel

```
MODULE 1 — DIAGNOSTIC              MODULE 2 — BACKUP
"Ca marche ?"                       "Sauvegarde les donnees"

check_ad_dns ──► AD/DNS OK ?        backup_database ──► dump SQL + SHA256
check_mysql  ──► MySQL OK ?         export_table_csv ──► CSV + SHA256
check_linux  ──► Services actifs ?
check_http   ──► HTTP/HTTPS OK ?


MODULE 3 — AUDIT
"Qu'est-ce qui est obsolete ?"

scan_network   ──► Qui est sur le reseau ?
list_os_eol    ──► Quelles dates EOL ?
audit_from_csv ──► Croiser inventaire × EOL
generate_report──► Rapport trie par urgence
```

---

## Rappels communs a tous les modules

- Chaque fonction retourne un resultat via `build_result()` (voir [04-interfaces.md](04-interfaces.md))
- Chaque fonction a un try/except — **jamais de crash**
- Les credentials viennent du `config.yaml` — **jamais de hardcode**
- Seuil WARNING partout : **> 80%** (CPU, RAM, Disque)
- Timeout par defaut : **10 secondes**
- Les resultats sont sauves dans `output/logs/` en JSON horodate
