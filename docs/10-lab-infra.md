# Infrastructure Lab — Proxmox

> Dossier : `infra/proxmox/`, `infra/post-install/`
> Rôle : Créer automatiquement le lab NordTransit (18 VMs) sur un serveur Proxmox.

## Vue d'ensemble

```
Réseau : 192.168.10.0/24 (bridge vmbr10)
Domaine : ntl.local
18 VMs : 7 Linux + 11 Windows
```

### Les machines principales

| VM | IP | OS | Rôle |
|----|----|----|------|
| DC01 | .10 | Win Server 2022 | Contrôleur de domaine principal (AD + DNS) |
| DC02 | .11 | Win Server 2019 | Contrôleur de domaine secondaire |
| WMS-DB | .21 | Ubuntu 20.04 | Base de données MySQL (WMS) |
| WMS-APP | .22 | Ubuntu 20.04 | Serveur applicatif |
| SRV-FILES | .30 | Win Server 2022 | Partage de fichiers |
| SRV-PRINT | .31 | Win Server 2019 | Serveur d'impression |
| + 7 autres | .32-.53 | Divers | NAS, Intranet, Backup, 5 postes clients |

## Workflow de déploiement

```
1. download-images.sh    Télécharge les ISOs Linux + drivers VirtIO
                         (les ISOs Windows sont à télécharger manuellement)

2. scan-proxmox.sh       Vérifie que les VMIDs et IPs sont libres
                         (évite les conflits avant de créer)

3. setup-lab.sh          Crée les 18 VMs depuis vms.csv
                         Configure le réseau (bridge + NAT)
                         Snapshots "clean-state" après install

4. Post-install          Automatique via cloud-init (Linux)
                         ou autounattend.xml (Windows)

5. Vérification          Ping toutes les VMs
                         Teste LDAP:389, MySQL:3306, SSH:22
```

## Ce que fait chaque script

### Scripts Proxmox (`infra/proxmox/`)

| Script | Rôle |
|--------|------|
| `config.env` | Variables de config (stockage, réseau, credentials) |
| `vms.csv` | Liste des 18 VMs (VMID, hostname, OS, IP, CPU, RAM, disk) |
| `images.conf` | Mapping OS → fichier ISO/image cloud |
| `download-images.sh` | Télécharge les images Linux et VirtIO |
| `scan-proxmox.sh` | Pré-vol : vérifie VMIDs libres, IPs disponibles, espace disque |
| `setup-lab.sh` | Crée tout le lab (VMs + réseau + snapshots) |
| `teardown-lab.sh` | Détruit tout le lab (avec confirmation) |

### Scripts post-install (`infra/post-install/`)

| Script | Machine | Ce qu'il fait |
|--------|---------|---------------|
| `setup-dc01.ps1` | DC01 | IP statique → installe AD/DNS → promeut en DC (ntl.local) |
| `setup-dc01-part2.ps1` | DC01 | Crée les OUs, utilisateurs test, groupes, ouvre le firewall |
| `dc02-ad-secondary.ps1` | DC02 | Attend DC01 → rejoint le domaine → réplication AD |
| `setup-wmsdb.sh` | WMS-DB | Installe MySQL + SSH → importe le schéma WMS → crée l'utilisateur |
| `setup-client01.ps1` | CLIENT-01 | IP statique → installe Python, Git, nmap via winget |
| `seed-wms.sql` | WMS-DB | Schéma BDD (tables shipments + inventory) + données démo |

## Architecture réseau

```
Internet
    │
    ▼
[Proxmox Host] ── vmbr0 (réseau physique)
    │
    ├── NAT (iptables MASQUERADE)
    │
    └── vmbr10 (192.168.10.0/24) ── réseau lab isolé
         │
         ├── .1   Gateway
         ├── .10  DC01 (AD/DNS primaire)
         ├── .11  DC02 (AD/DNS secondaire)
         ├── .21  WMS-DB (MySQL)
         ├── .22  WMS-APP
         ├── .30  SRV-FILES
         └── .50+ Postes clients
```

## Data-driven : ajouter/supprimer une VM

Tout passe par `vms.csv`. Pour ajouter une VM :

```csv
1060,MON-SERVEUR,ubuntu-2004,60,2,2048,20,setup-mon-serveur.sh
```

Colonnes : `VMID, hostname, os_key, ip_suffix, cores, ram_mb, disk_gb, post_install_script`

Puis relancer `setup-lab.sh`. C'est tout.
