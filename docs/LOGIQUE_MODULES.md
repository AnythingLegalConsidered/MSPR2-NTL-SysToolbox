# Logique complète des 3 modules

> Ce document explique ce que fait chaque module, fonction par fonction.
> Pas de code ici — juste la logique, les entrées, les sorties et le raisonnement.

---

## Module 1 — Diagnostic (`src/modules/diagnostic.py`)

**Responsable :** Blaise
**But :** Vérifier que les services critiques de NTL fonctionnent.

### 1.1 check_ad_dns()

**Cible :** DC01 (192.168.10.10)
**Question à laquelle on répond :** "Est-ce que l'Active Directory et le DNS tournent ?"

**Logique :**

```
1. Tester le port LDAP (389) sur DC01
   → Le port est ouvert ? L'AD est accessible.
   → Le port est fermé ? L'AD est down.

2. Résoudre "ntl.local" via le DNS de DC01
   → Ça résout ? Le DNS fonctionne.
   → Ça ne résout pas ? Le DNS est cassé.

3. Décider du status :
   ┌─────────────────────────────┬──────────┐
   │ LDAP OK + DNS OK            │ OK       │
   │ LDAP OK + DNS KO            │ WARNING  │
   │ LDAP KO (peu importe DNS)   │ CRITICAL │
   │ DC01 injoignable            │ UNKNOWN  │
   └─────────────────────────────┴──────────┘
```

**Utilise :** `check_port()` (port 389), `resolve_dns()` (ntl.local via DC01)
**Détails retournés :** `ldap: true/false`, `dns: true/false`, `dns_result: "192.168.10.10" ou null`

---

### 1.2 check_mysql()

**Cible :** WMS-DB (192.168.10.21)
**Question :** "Est-ce que MySQL répond et la base WMS est accessible ?"

**Logique :**

```
1. Se connecter à MySQL avec les credentials du config.yaml
   → Connexion OK ? Continuer.
   → Connexion KO ? Status CRITICAL.

2. Exécuter SHOW DATABASES
   → Vérifier que "wms" est dans la liste

3. Exécuter SHOW STATUS
   → Récupérer : uptime, threads connectés, nombre de requêtes

4. Décider du status :
   ┌──────────────────────────────┬──────────┐
   │ Connexion OK + base visible  │ OK       │
   │ Connexion OK + base absente  │ WARNING  │
   │ Connexion refusée            │ CRITICAL │
   │ Serveur injoignable          │ UNKNOWN  │
   └──────────────────────────────┴──────────┘
```

**Utilise :** `mysql-connector-python` (connexion + requêtes)
**Détails retournés :** `connected: true/false`, `databases: [...]`, `uptime: "..."`, `threads: N`, `questions: N`

---

### 1.3 check_windows_server()

**Cible :** DC01 (192.168.10.10) ou autre serveur Windows
**Question :** "Quelles sont les métriques du serveur Windows (CPU, RAM, disque) ?"

**Logique :**

```
1. Exécuter des commandes wmic via subprocess
   → CPU : wmic cpu get LoadPercentage
   → RAM : wmic OS get FreePhysicalMemory,TotalVisibleMemorySize
   → Disque : wmic logicaldisk get Size,FreeSpace

2. Calculer les pourcentages d'utilisation

3. Décider du status :
   ┌────────────────────────────────────┬──────────┐
   │ CPU < 80% ET RAM < 80% ET Disk < 80% │ OK       │
   │ Un des trois > 80%                    │ WARNING  │
   │ Commande échoue                       │ CRITICAL │
   │ Serveur injoignable                   │ UNKNOWN  │
   └────────────────────────────────────┴──────────┘
```

**Utilise :** `subprocess` (wmic) ou `psutil` si exécuté localement
**Détails retournés :** `cpu_percent: N`, `ram_percent: N`, `disk_percent: N`, `ram_total_mb: N`, `disk_total_gb: N`

---

### 1.4 check_ubuntu()

**Cible :** WMS-DB (192.168.10.21) ou autre serveur Ubuntu
**Question :** "Quel est l'état du serveur Ubuntu ?"

**Logique :**

```
1. Se connecter en SSH avec paramiko (credentials du config.yaml)

2. Exécuter des commandes à distance :
   → lsb_release -a     → Version de l'OS
   → uptime              → Temps de fonctionnement
   → free -m             → RAM utilisée / totale
   → df -h               → Espace disque
   → systemctl status mysql  → État du service MySQL

3. Parser les résultats et calculer les pourcentages

4. Décider du status :
   ┌────────────────────────────────────┬──────────┐
   │ RAM < 80% ET Disk < 80%              │ OK       │
   │ RAM > 80% OU Disk > 80%              │ WARNING  │
   │ SSH échoue                            │ CRITICAL │
   │ Serveur injoignable                   │ UNKNOWN  │
   └────────────────────────────────────┴──────────┘
```

**Utilise :** `paramiko` (SSH), parsing des sorties texte
**Détails retournés :** `os_version: "..."`, `uptime: "..."`, `ram_percent: N`, `disk_percent: N`, `mysql_status: "active/inactive"`

---

## Module 2 — Backup (`src/modules/backup.py`)

**Responsable :** Ojvind
**But :** Sauvegarder la base WMS et exporter des tables en CSV.

### 2.1 backup_database()

**Cible :** Base `wms` sur WMS-DB
**Question :** "Faire un dump complet de la base et vérifier son intégrité."

**Logique :**

```
1. Se connecter en SSH à WMS-DB

2. Exécuter mysqldump via SSH :
   → mysqldump -u wms_user -p wms > dump.sql
   → Résultat récupéré en local

3. Sauvegarder le fichier :
   → Nom : wms_20260226_143000.sql
   → Dossier : output/backups/

4. Vérifier l'intégrité :
   → Calculer le hash SHA256 du fichier
   → Vérifier que la taille > 0 octets

5. Décider du status :
   ┌────────────────────────────────────┬──────────┐
   │ Fichier créé + taille > 0 + SHA256   │ OK       │
   │ Fichier vide                          │ CRITICAL │
   │ mysqldump échoue                      │ CRITICAL │
   │ SSH échoue                            │ UNKNOWN  │
   └────────────────────────────────────┴──────────┘
```

**Utilise :** `paramiko` (SSH), `subprocess` (mysqldump), `hashlib` (SHA256)
**Détails retournés :** `file_path: "..."`, `file_size_bytes: N`, `sha256: "abc123..."`, `duration_seconds: N`

---

### 2.2 export_table_csv()

**Cible :** Une table de la base `wms` (ex: `shipments`, `inventory`)
**Question :** "Exporter le contenu d'une table en fichier CSV."

**Logique :**

```
1. Se connecter à MySQL avec mysql-connector-python

2. Exécuter : SELECT * FROM <table>

3. Écrire le résultat en CSV :
   → Nom : shipments_20260226_143000.csv
   → Dossier : output/backups/
   → Encodage : UTF-8
   → Séparateur : virgule (,)
   → Première ligne = noms des colonnes

4. Calculer le SHA256

5. Décider du status :
   ┌─────────────────────────────┬──────────┐
   │ Fichier créé + données OK   │ OK       │
   │ Table vide (0 lignes)       │ WARNING  │
   │ Table inexistante           │ CRITICAL │
   │ Connexion MySQL échoue      │ UNKNOWN  │
   └─────────────────────────────┴──────────┘
```

**Utilise :** `mysql-connector-python` (SELECT), `csv` (écriture), `hashlib` (SHA256)
**Détails retournés :** `file_path: "..."`, `row_count: N`, `columns: [...]`, `sha256: "..."`, `table: "shipments"`

---

## Module 3 — Audit (`src/modules/audit.py`)

**Responsable :** Zaid
**But :** Scanner le réseau, identifier les OS obsolètes, générer un rapport.

### 3.1 scan_network()

**Cible :** Plage réseau (ex: 192.168.10.0/24)
**Question :** "Quelles machines sont sur le réseau et quels services tournent ?"

**Logique :**

```
1. Détecter si on a les droits admin
   → Admin : scan complet (nmap -sV -O)
   → Pas admin : scan dégradé (nmap -sT -sV) + WARNING

2. Scanner la plage réseau avec python-nmap

3. Pour chaque machine trouvée, récupérer :
   → IP
   → Hostname (si détectable)
   → OS détecté (si droits admin)
   → Ports ouverts + services

4. Décider du status :
   ┌──────────────────────────────┬──────────┐
   │ Scan terminé, machines trouvées │ OK       │
   │ Scan dégradé (pas admin)        │ WARNING  │
   │ nmap pas installé               │ CRITICAL │
   │ Réseau injoignable              │ UNKNOWN  │
   └──────────────────────────────┴──────────┘
```

**Utilise :** `python-nmap` (scan réseau)
**Détails retournés :** `hosts_found: N`, `hosts: [{ip, hostname, os, ports: [...]}]`, `scan_type: "full/degraded"`

---

### 3.2 list_os_eol()

**Cible :** Tous les OS de la base EOL locale
**Question :** "Quelles sont les dates de fin de vie de chaque OS ?"

**Logique :**

```
1. Lire le fichier data/eol_database.json

2. Pour chaque OS, calculer :
   → Jours restants avant EOL
   → Status : EXPIRÉ / BIENTÔT (< 6 mois) / OK

3. Trier par urgence : EXPIRÉ en premier, puis BIENTÔT, puis OK

4. Status toujours OK (c'est juste une consultation de données)
```

**Source de données :** `data/eol_database.json` — fichier local, pas d'appel réseau
**Détails retournés :** `os_list: [{name, eol_date, days_remaining, status: "expired/soon/ok"}]`

---

### 3.3 audit_from_csv()

**Cible :** Fichier CSV d'inventaire (ex: `data/sample_inventory.csv`)
**Question :** "Quelles machines de notre parc ont un OS obsolète ?"

**Logique :**

```
1. Lire le CSV d'inventaire (hostname, os_name, os_version, role)

2. Pour chaque ligne du CSV :
   → Reconstituer le nom complet de l'OS (ex: "Windows Server" + "2022" → "Windows Server 2022")
   → Chercher dans eol_database.json
   → Calculer les jours restants

3. Classer chaque machine :
   ┌──────────────────────────────────────┬──────────┐
   │ EOL dépassée                          │ EXPIRÉ   │
   │ EOL dans moins de 6 mois              │ BIENTÔT  │
   │ EOL dans plus de 6 mois               │ OK       │
   │ OS pas trouvé dans la base EOL        │ INCONNU  │
   └──────────────────────────────────────┴──────────┘

4. Exemple avec l'inventaire NTL :
   SRV-PRINT (Win Server 2008 R2) → EXPIRÉ (depuis 2023)
   PC-QUAI-WH1 (Windows 7)         → EXPIRÉ (depuis 2023)
   SRV-FILE (Win Server 2012 R2)   → BIENTÔT (oct 2026)
   DC01 (Win Server 2022)           → OK (jusqu'en 2031)
```

**Utilise :** `csv` (lecture), `json` (base EOL), `datetime` (calcul des jours)
**Détails retournés :** `total_hosts: N`, `expired: N`, `soon: N`, `ok: N`, `unknown: N`, `hosts: [...]`

---

### 3.4 generate_report()

**Cible :** Résultat combiné de scan_network + audit_from_csv
**Question :** "Générer un rapport complet d'obsolescence, trié par criticité."

**Logique :**

```
1. Lancer audit_from_csv() (ou utiliser les résultats déjà en mémoire)

2. Trier les résultats par criticité :
   → D'abord les EXPIRÉ (rouge)
   → Puis les BIENTÔT (orange)
   → Puis les OK (vert)

3. Générer 2 sorties :
   → Tableau rich dans le terminal (coloré, lisible)
   → Fichier JSON dans output/reports/

4. Le rapport contient pour chaque machine :
   → Hostname
   → OS actuel
   → Date EOL
   → Jours restants (ou "expiré depuis X jours")
   → Rôle dans l'infra
   → Recommandation (mettre à jour vers quelle version)
```

**Utilise :** `rich` (affichage coloré), `json` (export)
**Détails retournés :** `report_path: "..."`, `summary: {expired: N, soon: N, ok: N}`, `generated_at: "..."`

---

## Résumé visuel

```
MODULE 1 — DIAGNOSTIC              MODULE 2 — BACKUP
"Ça marche ?"                       "Sauvegarde les données"

check_ad_dns ──► AD/DNS OK ?        backup_database ──► dump SQL + SHA256
check_mysql  ──► MySQL OK ?         export_table_csv ──► CSV + SHA256
check_windows──► CPU/RAM/Disk ?
check_ubuntu ──► SSH + métriques ?


MODULE 3 — AUDIT
"Qu'est-ce qui est obsolète ?"

scan_network   ──► Qui est sur le réseau ?
list_os_eol    ──► Quelles dates EOL ?
audit_from_csv ──► Croiser inventaire × EOL
generate_report──► Rapport trié par urgence
```

---

## Rappels communs à tous les modules

- Chaque fonction retourne un résultat via `build_result()` (voir [INTERFACES.md](INTERFACES.md))
- Chaque fonction a un try/except — **jamais de crash**
- Les credentials viennent du `config.yaml` — **jamais de hardcode**
- Seuil WARNING partout : **> 80%** (CPU, RAM, Disque)
- Timeout par défaut : **10 secondes**
- Les résultats sont sauvés dans `output/logs/` en JSON horodaté
