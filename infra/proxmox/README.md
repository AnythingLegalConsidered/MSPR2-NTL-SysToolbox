# Lab Proxmox — NTL-SysToolbox (18 VMs)

## Quick Start — Mode API (pas de shell Proxmox)

Si vous n'avez pas de shell root sur le Proxmox (compte etudiant), utilisez
le mode API depuis une VM "deployer".

### Etape 0 : Creer le deployer + API token

1. **Web UI Proxmox** : Creer une VM Debian 12 minimale (1 core, 1 GB RAM, 10 GB)
2. **Web UI** : `Datacenter > Permissions > API Tokens > Add`
   - User : votre compte (ex: `etudiant@pam`)
   - Token ID : `ntl-lab`
   - **Decocher** "Privilege Separation"
   - **Copier le secret** (affiche une seule fois)
3. **Console du deployer** (via noVNC dans le web UI) :
   ```bash
   apt update && apt install -y curl python3 genisoimage git
   git clone <votre-repo> && cd MSPR2/infra/proxmox
   cp config.env config.local.env
   nano config.local.env   # Remplir PVE_HOST, PVE_NODE, PVE_TOKEN_ID, PVE_TOKEN_SECRET
   ```

### Etape 1-6 : Deployer le lab

```bash
# 1. Telecharger les images Linux via API
bash download-images-api.sh

# 2. Uploader les ISOs Windows via le web UI
#    (Datacenter > Storage > local > Upload)

# 3. Creer les 18 VMs via API
bash setup-lab-api.sh

# 4. Demarrer par vagues
bash orchestrate-lab-api.sh demo    # essential | demo | full

# 5. Verifier
bash verify-lab.sh demo
```

### Quick Start — Mode local (shell root sur Proxmox)

Si vous avez un acces shell root (SSH ou Node > Shell dans le web UI) :

```bash
cp config.env config.local.env && nano config.local.env
bash download-images.sh
bash scan-proxmox.sh --local
bash setup-lab.sh
bash orchestrate-lab.sh demo
bash verify-lab.sh demo
```

Linux = cloud-init, Windows = autounattend.xml. Pas d'install manuelle.

### Profils de demarrage

| Profil | VMs | RAM | Usage |
|--------|-----|-----|-------|
| `essential` | 3 | ~10 GB | Test rapide (DC01 + WMS-DB + CLIENT-01) |
| `demo` | 11 | ~27 GB | Soutenance (variete OS + services) |
| `full` | 18 | ~45 GB | Lab complet |

## Architecture

```
scripts/
  proxmox/
    config.env             # Template config (copier en .local.env)
    vms.csv                # Definition des 18 VMs (1 ligne = 1 VM)
    images.conf            # Mapping os_key -> image/template
    profiles.conf          # Profils de demarrage (essential/demo/full)
    # --- Mode local (shell root sur Proxmox) ---
    setup-lab.sh           # Cree tout : bridge + 18 VMs (qm)
    orchestrate-lab.sh     # Demarre les VMs par vagues (qm)
    download-images.sh     # Telecharge cloud images + VirtIO (wget)
    scan-proxmox.sh        # Pre-flight : verifie conflits/ressources
    teardown-lab.sh        # Supprime tout

    # --- Mode API (depuis deployer VM, sans shell Proxmox) ---
    setup-lab-api.sh       # Cree tout via API REST (curl)
    orchestrate-lab-api.sh # Demarre par vagues via API
    download-images-api.sh # Telecharge images via API

    # --- Communs ---
    verify-lab.sh          # Dashboard de verification des services
    lib/
      common.sh            # Fonctions partagees
      wait-service.sh      # Helpers : wait_for_port, wait_for_vm_agent
      proxmox-api.sh       # Wrapper API REST Proxmox (curl)
      create-linux-vm.sh   # Creation VM Linux — mode local (qm)
      create-windows-vm.sh # Creation VM Windows — mode local (qm)
      gen-autounattend.sh  # Genere XML depuis template
      gen-cloud-init.sh    # Genere user-data depuis template
  templates/
    autounattend/          # 5 templates XML (par version Windows)
    cloud-init/            # 3 templates YAML (Ubuntu/Debian/CentOS)
  post-install/            # Scripts post-install (AD, MySQL, etc.)
    setup-dc01.ps1         # DC01 : foret AD ntl.local + DNS
    setup-dc01-part2.ps1   # DC01 : OUs, users, groupes, firewall
    dc02-ad-secondary.ps1  # DC02 : replication AD depuis DC01
    setup-wmsdb.sh         # WMS-DB : MySQL + SSH + seed data
    setup-client01.ps1     # CLIENT-01 : domain join + outils (Python, Git, nmap)
    setup-srvfile.ps1      # SRV-FILE : SMB shares + domain join
    setup-wmsapp.sh        # WMS-APP : Nginx + page statique WMS
    setup-nas.sh           # NAS-01 : NFS + SMB exports backup
    setup-srvbackup.sh     # SRV-BACKUP : cron mysqldump quotidien
    setup-domainjoin.ps1   # Generique : domain join pour clients Windows
```

## Les 18 VMs

| VMID | Hostname | OS | IP | Role |
|------|----------|----|----|------|
| 1010 | DC01 | Win Server 2022 | .10 | AD/DNS principal |
| 1011 | DC02 | Win Server 2019 | .11 | DC secondaire |
| 1012 | SRV-FILE | Win Server 2012 R2 | .12 | File Server |
| 1013 | SRV-PRINT | Win Server 2008 R2 | .13 | Print Server |
| 1015 | SUPER-01 | Win Server 2016 | .15 | Supervision |
| 1021 | WMS-DB | Ubuntu 20.04 | .21 | MySQL WMS |
| 1022 | WMS-APP | Ubuntu 20.04 | .22 | App WMS |
| 1030 | IPBX-VM | CentOS 7 | .30 | Telephonie |
| 1040 | NAS-01 | Debian 10 | .40 | Backup NAS |
| 1041 | SRV-INTRANET | Debian 11 | .41 | Wiki interne |
| 1042 | SRV-BACKUP | Ubuntu 16.04 | .42 | Sauvegarde |
| 1043 | SRV-CDK | Ubuntu 18.04 | .43 | Cross-dock |
| 1050 | PC-SIEGE-01 | Windows 11 | .50 | Poste siege |
| 1051 | PC-SIEGE-02 | Windows 11 | .51 | Poste siege |
| 1052 | PC-COMPTA-01 | Windows 10 | .52 | Comptabilite |
| 1060 | PC-QUAI-WH1 | Windows 7 | .60 | Terminal Lens |
| 1061 | PC-QUAI-WH2 | Windows 7 | .61 | Terminal Valenciennes |
| 1062 | PC-QUAI-WH3 | Windows 10 | .62 | Terminal Arras |

Reseau : `192.168.10.0/24` sur bridge `vmbr10`

## Comment ca marche

### Linux (7 VMs) — 100% automatique
1. `setup-lab.sh` lit `vms.csv`
2. Pour chaque VM Linux : `qm create` + cloud image + cloud-init
3. Cloud-init configure hostname, IP, user, paquets, post-install
4. VM prete en ~5 min

### Windows (11 VMs) — zero-click
1. `gen-autounattend.sh` genere un `autounattend.xml` par VM
2. L'XML est empaquete en ISO via `genisoimage`
3. L'ISO est attachee a la VM
4. Windows lit l'XML au boot -> install sans aucun clic
5. `<FirstLogonCommands>` execute le script post-install (AD, etc.)

## Orchestration (vagues de demarrage)

`orchestrate-lab.sh` demarre les VMs dans l'ordre des dependances :

```
Vague 1 — Linux (cloud-init, ~5 min)
  WMS-DB, WMS-APP, NAS-01, SRV-BACKUP, IPBX-VM, SRV-CDK...

Vague 2 — Domain Controller
  DC01 → attente LDAP:389 (30-60 min si premiere install)
  DC02 → son post-install attend DC01 tout seul

Vague 3 — Serveurs Windows (SRV-FILE, SRV-PRINT, SUPER-01)
  SRV-FILE → domain join + SMB shares automatique

Vague 4 — Clients Windows (domain join automatique)

Vague 5 — Verification (appelle verify-lab.sh)
```

### Verification

```bash
bash verify-lab.sh demo
```

Affiche un dashboard avec ping, ports, AD, MySQL et score global.

## Data-driven : modifier le lab

Ajouter une VM = ajouter une ligne dans `vms.csv` :
```csv
1070,MON-VM,ubuntu-2004,70,2,2048,20,
```

Supprimer une VM = supprimer ou commenter la ligne.

## Configurer config.local.env

```bash
# Trouver votre storage
pvesm status

# Trouver votre interface NAT
ip route | grep default

# Verifier les VM IDs libres
qm list
```

## ISOs Windows (download manuel)

Les ISOs Windows doivent etre telechargees manuellement :
- Server 2022/2019/2016 : Microsoft Evaluation Center
- Server 2012 R2/2008 R2 : Microsoft Evaluation Center
- Windows 10/11 : Microsoft Software Download
- Windows 7 : votre propre source

Upload via le **web UI** : `Datacenter > Storage > local > Upload`

Ou via SCP (si acces shell) :
```bash
scp MonISO.iso root@proxmox:/var/lib/vz/template/iso/
```

Noms attendus (voir `images.conf`) :
```
win2022_eval.iso, win2019_eval.iso, win2016_eval.iso
win2012r2_eval.iso, win2008r2_eval.iso
win11.iso, win10.iso, win7.iso
```

## Replique sur un autre Proxmox

### Option A : Exporter/Importer
```bash
# Source : exporter toutes les VMs
vzdump $(awk -F, 'NR>1{printf "%s ",$1}' vms.csv) --compress zstd --storage local

# Destination : importer
for f in /chemin/vzdump-qemu-*.vma.zst; do
    vmid=$(echo "$f" | grep -oP '(?<=qemu-)\d+')
    qmrestore "$f" "$vmid" --storage local-lvm
done
```

### Option B : Relancer le setup
```bash
bash download-images.sh
bash setup-lab.sh
```

## Credentials

| Service | User | Password |
|---------|------|----------|
| Linux SSH | sysadmin | SysAdm2026! |
| Windows Admin | Administrator | NTL@dmin2026! |
| AD Domain | ntl.local | NTL@dmin2026! |
| MySQL wms | wms_user | WmsP@ss2026 |

## Troubleshooting

**VM ID deja utilisee** : Modifiez le VMID dans `vms.csv`

**Cloud-init custom ne marche pas** : Verifiez snippet storage (`pvesm status --content snippets`)

**Pas d'Internet** : Verifiez `ENABLE_NAT=yes` et `NAT_INTERFACE` dans config

**Windows ne detecte pas le disque** : VirtIO ISO manquante. `download-images.sh` la telecharge.

**autounattend ne fonctionne pas** : Verifiez `genisoimage` installe (`apt install genisoimage`)
