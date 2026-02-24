# Lab Proxmox — NTL-SysToolbox

## Quick Start

```bash
# 1. Copier et adapter la config
cp config.env config.local.env
nano config.local.env   # <-- REMPLIR VOS VALEURS

# 2. Télécharger les images (sur le Proxmox)
bash download-images.sh

# 3. Créer le lab
bash setup-lab.sh

# 4. Installer les Windows manuellement (console noVNC)
# 5. Lancer les scripts post-install PowerShell sur chaque Windows
```

## Fichiers

| Fichier | Rôle |
|---------|------|
| `config.env` | **Template** de config — NE PAS MODIFIER directement |
| `config.local.env` | **Votre config** — copiée depuis config.env, adaptée à votre Proxmox |
| `setup-lab.sh` | Crée le bridge + les 5 VMs |
| `download-images.sh` | Télécharge les cloud images Ubuntu + VirtIO drivers |
| `teardown-lab.sh` | Supprime toutes les VMs + bridge |

## Comment remplir config.local.env

### 1. Trouver votre storage

```bash
pvesm status
```

Cherchez le storage de type `lvmthin`, `zfspool`, ou `dir`. C'est votre `STORAGE`.
Cherchez le storage qui contient les ISOs (type `dir`). C'est votre `ISO_STORAGE`.

### 2. Trouver votre interface NAT

```bash
ip route | grep default
```

Le "dev XXX" est votre `NAT_INTERFACE` (souvent `vmbr0`).

### 3. Vérifier les VM IDs disponibles

```bash
qm list
```

Si un des IDs (1010, 1012, 1018, 1021, 1050) est déjà pris, changez-le dans config.local.env.

### 4. ISOs Windows

Téléchargez manuellement depuis Microsoft Evaluation Center :
- **Windows Server 2022** : https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2022
- **Windows Server 2012 R2** : https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2012-r2
- **Windows 10** : https://www.microsoft.com/en-us/software-download/windows10ISO

Uploadez les ISOs sur le Proxmox :
```bash
scp MonISO.iso root@proxmox:/var/lib/vz/template/iso/
```

Puis renseignez les noms dans config.local.env :
```bash
ISO_WIN2022="win2022_eval.iso"
ISO_WIN10="win10.iso"
ISO_WIN2012="win2012r2_eval.iso"
```

## Architecture du lab

```
Bridge vmbr10 (192.168.10.0/24)
|
+-- .10  DC01          Windows Server 2022  (AD/DNS)
+-- .12  SRV-OLD       Windows Server 2012  (Legacy — pour audit)
+-- .18  SRV-LEGACY    Ubuntu 18.04         (Legacy — pour audit)
+-- .21  WMS-DB        Ubuntu 20.04         (MySQL + SSH)
+-- .50  CLIENT-01     Windows 10           (Poste client)
```

## Après le setup

### VMs Linux (automatiques)
Rien à faire. Cloud-init configure tout :
- **WMS-DB** : MySQL installé, BDD `wms` peuplée, SSH actif
- **SRV-LEGACY** : juste allumée et pingable

Attendez ~5 min après le démarrage pour que cloud-init finisse.

### VMs Windows (manuelles)

1. **DC01** : Installer Windows Server 2022 via noVNC, puis :
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process
   .\setup-dc01.ps1        # IP + AD DS + DNS (reboot auto)
   .\setup-dc01-part2.ps1  # OUs + users (après reboot)
   ```

2. **CLIENT-01** : Installer Windows 10 via noVNC, puis :
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process
   .\setup-client01.ps1    # IP + Python + Git + nmap
   ```

3. **SRV-OLD** : Installer Windows Server 2012 R2, configurer IP `.12` manuellement. C'est tout.

## Réplique sur un autre Proxmox

### Option A : Exporter/Importer les VMs
```bash
# Sur le Proxmox source
vzdump 1010 1012 1018 1021 1050 --compress zstd --storage local

# Copier les fichiers .vma.zst (clé USB, SCP, etc.)

# Sur le Proxmox destination
qmrestore /chemin/vzdump-qemu-1010-*.vma.zst 1010 --storage local-lvm
qmrestore /chemin/vzdump-qemu-1012-*.vma.zst 1012 --storage local-lvm
qmrestore /chemin/vzdump-qemu-1018-*.vma.zst 1018 --storage local-lvm
qmrestore /chemin/vzdump-qemu-1021-*.vma.zst 1021 --storage local-lvm
qmrestore /chemin/vzdump-qemu-1050-*.vma.zst 1050 --storage local-lvm
```

Prérequis : même bridge `vmbr10` configuré sur les deux Proxmox.

### Option B : Relancer le setup
```bash
# Copier config.local.env adapté au nouveau Proxmox
bash setup-lab.sh
```

## Credentials

| Service | User | Password |
|---------|------|----------|
| WMS-DB SSH | sysadmin | SysAdm2026! |
| MySQL wms | wms_user | WmsP@ss2026 |
| AD Admin | Administrator | (défini à l'install Windows) |
| AD Safe Mode | - | NTL@dmin2026! |
| AD User | wms-service | WmsS3rv!ce |
| AD User | admin-ntl | Adm1n@NTL! |

## Troubleshooting

**"VM ID already exists"** : Changez les VMIDs dans config.local.env

**Cloud-init ne fonctionne pas** : Vérifiez que vous avez un snippet storage (`pvesm status --content snippets`). Sinon, lancez le setup manuellement via SSH.

**Pas d'Internet dans les VMs** : Vérifiez que `ENABLE_NAT=yes` et que `NAT_INTERFACE` est correct.

**Windows ne détecte pas le disque** : Les drivers VirtIO ne sont pas chargés. Pendant l'install, cliquez "Load driver" et pointez vers le CD VirtIO (D:\vioscsi\w10\amd64 ou similaire).
