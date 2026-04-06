# Demo NTL-SysToolbox — Homelab (pve02)

Guide pour lancer la toolbox sur le lab homelab en fallback de l'ecole.

## Pre-requis

- PC fixe connecte au reseau local (192.168.2.0/24)
- pve02 allume (les VMs demarrent automatiquement avec)
- Route Windows active : `route add 172.16.132.0 mask 255.255.255.0 192.168.2.4 if 15 -p`
- MySQL client installe (`winget install Oracle.MySQL`)
- nmap installe
- PATH inclut : `C:\Program Files\MySQL\MySQL Server 8.4\bin`

## Lab : 2 VMs sur pve02

| VM | VMID | IP | Services | Credentials |
|----|------|----|----------|-------------|
| DC01 | 110 | 172.16.132.10 | Samba AD DC (ntl.local), DNS, LDAP, Kerberos | Administrator / **** |
| WMS-DB | 120 | 172.16.132.20 | MySQL 8.0 (base `wms`), SSH | sysadmin / **** |

AD users : `wms-service`, `admin-ntl`, `j.dupont`, `m.martin`
MySQL : 8 shipments, 6 inventory

## Avant la demo

```bash
# Verifier que tout est up
bash start-demo.sh
```

Tous les checks doivent etre `[OK]`. Si un check echoue :
- VMs eteintes → Proxmox Web UI `https://192.168.2.4:8006` > demarrer VM 110 + 120
- Route perdue → relancer `route add 172.16.132.0 mask 255.255.255.0 192.168.2.4 if 15` en admin
- Snapshot clean → Proxmox > VM > Snapshots > `clean-state` > Rollback

## Lancer la toolbox

```bash
cd C:\Users\Dharma\Documents\Pro\Ecole\Rendu\MSPR\MSPR2
python -m src.main
```

## Scenario de demo (5 min)

### 1. Diagnostic — Verifier AD/DNS (Choix 1 > 1)

```
Menu principal > 1 (Diagnostic) > 1 (Verifier AD/DNS)
IP du DC : [Entree pour defaut = 172.16.132.10]
```

**Ce que ca fait :** Resout `ntl.local` via le DNS du DC, scanne les ports AD (53, 88, 389, 445, 3268), teste le bind LDAP.
**Resultat attendu :** WARNING (DNS OK, Ports OK, LDAP OK, WinRM non configure = normal).

### 2. Diagnostic — Verifier MySQL (Choix 1 > 2)

```
Menu principal > 1 (Diagnostic) > 2 (Verifier MySQL)
IP du serveur : [Entree pour defaut = 172.16.132.20]
```

**Ce que ca fait :** Connexion TCP sur le port 3306, recupere la version MySQL via le banner.
**Resultat attendu :** OK — MySQL 8.0.45 detecte.

### 3. Diagnostic — Services Linux (Choix 1 > 3)

```
Menu principal > 1 (Diagnostic) > 3 (Verifier services Linux)
IP du serveur : 172.16.132.10
```

**Ce que ca fait :** Scanne les ports configures (22, 53, 88, 389, 3306) et identifie les services ouverts.
**Resultat attendu :** OK — 4 services (SSH, DNS, Kerberos, LDAP) sur DC01.

### 4. Backup — Dump SQL (Choix 2 > 1)

```
Menu principal > 2 (Backup) > 1 (Backup base de donnees)
Base a sauvegarder : [Entree pour defaut = wms]
```

**Ce que ca fait :** Execute `mysqldump` sur la base `wms` de WMS-DB (172.16.132.20), sauvegarde le .sql dans `output/backups/`.
**Resultat attendu :** OK — fichier `wms_YYYYMMDD_HHMMSS.sql` cree (~4 KB).

### 5. Audit — Scanner reseau (Choix 3 > 1)

```
Menu principal > 3 (Audit) > 1 (Scanner le reseau)
Plage reseau : [Entree pour defaut = 172.16.132.0/24]
```

**Ce que ca fait :** Lance un scan nmap sur le subnet, detecte les hosts up et leurs ports ouverts.
**Resultat attendu :** OK — 2 hosts trouves (DC01 + WMS-DB) avec leurs services.

### 6. Quitter (Choix 0)

## Depannage rapide

| Probleme | Solution |
|----------|----------|
| `ping 172.16.132.10` timeout | Verifier route : `route print \| findstr 172.16.132` |
| VM eteinte | SSH pve02 : `qm start 110` / `qm start 120` |
| MySQL refuse connexion | SSH WMS-DB : `sudo systemctl restart mysql` |
| Samba plante | SSH DC01 : `sudo systemctl restart samba-ad-dc` |
| Tout casse | Rollback snapshot : `qm rollback 110 clean-state && qm rollback 120 clean-state && qm start 110 && qm start 120` |

## Architecture

```mermaid
graph TD
    subgraph "Reseau local 192.168.2.0/24"
        PC["PC Fixe<br/>192.168.2.2"]
        PVE["pve02<br/>192.168.2.4<br/>(vmbr0)"]
    end

    subgraph "Reseau NTL virtuel 172.16.132.0/24"
        GW["pve02 - vmbr1<br/>172.16.132.254<br/>(gateway)"]
        DC01["DC01<br/>172.16.132.10<br/>Samba AD/DNS/LDAP"]
        WMS["WMS-DB<br/>172.16.132.20<br/>MySQL 8.0"]
    end

    subgraph "Oral jour J"
        LAPTOP["PC Portable Pro"]
    end

    LAPTOP -->|"AnyDesk"| PC
    PC -->|"route add 172.16.132.0<br/>via 192.168.2.4"| PVE
    PVE ---|"bridge interne"| GW
    GW --- DC01
    GW --- WMS

    PC -.->|"python -m src.main"| DC01
    PC -.->|"mysqldump / nmap"| WMS

    style PC fill:#4a9eff,color:#fff
    style PVE fill:#e67e22,color:#fff
    style DC01 fill:#2ecc71,color:#fff
    style WMS fill:#2ecc71,color:#fff
    style LAPTOP fill:#9b59b6,color:#fff
    style GW fill:#e67e22,color:#fff
```
