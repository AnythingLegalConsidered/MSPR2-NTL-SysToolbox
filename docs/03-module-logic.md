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

**Exemple concret : check_ad_dns**

```python
def check_ad_dns(config: dict, target: str) -> dict:
    try:
        ldap_ok = check_port(target, 389, timeout=config.get("general", {}).get("timeout", 10))
        dns_result = resolve_dns("ntl.local", dns_server=target)
        dns_ok = dns_result is not None

        if ldap_ok and dns_ok:
            status, code = "OK", EXIT_OK
            msg = "AD et DNS operationnels"
        elif not ldap_ok:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"LDAP injoignable sur {target}:389"
        else:
            status, code = "WARNING", EXIT_WARNING
            msg = f"DNS ne resout pas ntl.local"

        return build_result(
            module=MODULE_NAME,
            function="check_ad_dns",
            status=status,
            exit_code=code,
            target=target,
            details={"ldap": ldap_ok, "dns": dns_ok, "dns_result": dns_result},
            message=msg,
        )

    except Exception as e:
        logger.error("check_ad_dns failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="check_ad_dns",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(e)},
            message=f"Impossible de verifier {target}: {e}",
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

**Fichier :** `src/modules/diagnostic.py`
**Responsable :** Blaise
**But :** Verifier que les services critiques de NTL fonctionnent.

### 1.1 check_ad_dns()

**Cible :** DC01 (192.168.10.10)
**Question :** "Est-ce que l'Active Directory et le DNS tournent ?"

**Logique :**

```
1. Tester le port LDAP (389) sur DC01
   → Le port est ouvert ? L'AD est accessible.
   → Le port est ferme ? L'AD est down.

2. Resoudre "ntl.local" via le DNS de DC01
   → Ca resout ? Le DNS fonctionne.
   → Ca ne resout pas ? Le DNS est casse.

3. Decider du status :
   ┌─────────────────────────────┬──────────┐
   │ LDAP OK + DNS OK            │ OK       │
   │ LDAP OK + DNS KO            │ WARNING  │
   │ LDAP KO (peu importe DNS)   │ CRITICAL │
   │ DC01 injoignable            │ UNKNOWN  │
   └─────────────────────────────┴──────────┘
```

**Utilise :** `check_port()` (port 389), `resolve_dns()` (ntl.local via DC01)
**Details retournes :** `ldap: true/false`, `dns: true/false`, `dns_result: "192.168.10.10" ou null`

---

### 1.2 check_mysql()

**Cible :** WMS-DB (192.168.10.21)
**Question :** "Est-ce que MySQL repond et la base WMS est accessible ?"

**Logique :**

```
1. Se connecter a MySQL avec les credentials du config.yaml
   → Connexion OK ? Continuer.
   → Connexion KO ? Status CRITICAL.

2. Executer SHOW DATABASES
   → Verifier que "wms" est dans la liste

3. Executer SHOW STATUS
   → Recuperer : uptime, threads connectes, nombre de requetes

4. Decider du status :
   ┌──────────────────────────────┬──────────┐
   │ Connexion OK + base visible  │ OK       │
   │ Connexion OK + base absente  │ WARNING  │
   │ Connexion refusee            │ CRITICAL │
   │ Serveur injoignable          │ UNKNOWN  │
   └──────────────────────────────┴──────────┘
```

**Utilise :** `mysql-connector-python` (connexion + requetes)
**Details retournes :** `connected: true/false`, `databases: [...]`, `uptime: "..."`, `threads: N`, `questions: N`

---

### 1.3 check_windows_server()

**Cible :** DC01 (192.168.10.10) ou autre serveur Windows
**Question :** "Quelles sont les metriques du serveur Windows (CPU, RAM, disque) ?"

**Logique :**

```
1. Executer des commandes wmic via subprocess
   → CPU : wmic cpu get LoadPercentage
   → RAM : wmic OS get FreePhysicalMemory,TotalVisibleMemorySize
   → Disque : wmic logicaldisk get Size,FreeSpace

2. Calculer les pourcentages d'utilisation

3. Decider du status :
   ┌────────────────────────────────────────┬──────────┐
   │ CPU < 80% ET RAM < 80% ET Disk < 80%  │ OK       │
   │ Un des trois > 80%                     │ WARNING  │
   │ Commande echoue                        │ CRITICAL │
   │ Serveur injoignable                    │ UNKNOWN  │
   └────────────────────────────────────────┴──────────┘
```

**Utilise :** `subprocess` (wmic) ou `psutil` si execute localement
**Details retournes :** `cpu_percent: N`, `ram_percent: N`, `disk_percent: N`, `ram_total_mb: N`, `disk_total_gb: N`

---

### 1.4 check_ubuntu()

**Cible :** WMS-DB (192.168.10.21) ou autre serveur Ubuntu
**Question :** "Quel est l'etat du serveur Ubuntu ?"

**Logique :**

```
1. Se connecter en SSH avec paramiko (credentials du config.yaml)

2. Executer des commandes a distance :
   → lsb_release -a     → Version de l'OS
   → uptime              → Temps de fonctionnement
   → free -m             → RAM utilisee / totale
   → df -h               → Espace disque
   → systemctl status mysql  → Etat du service MySQL

3. Parser les resultats et calculer les pourcentages

4. Decider du status :
   ┌────────────────────────────────────┬──────────┐
   │ RAM < 80% ET Disk < 80%           │ OK       │
   │ RAM > 80% OU Disk > 80%           │ WARNING  │
   │ SSH echoue                        │ CRITICAL │
   │ Serveur injoignable               │ UNKNOWN  │
   └────────────────────────────────────┴──────────┘
```

**Utilise :** `paramiko` (SSH), parsing des sorties texte
**Details retournes :** `os_version: "..."`, `uptime: "..."`, `ram_percent: N`, `disk_percent: N`, `mysql_status: "active/inactive"`

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

**Fichier :** `src/modules/audit.py`
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
check_windows──► CPU/RAM/Disk ?
check_ubuntu ──► SSH + metriques ?


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
