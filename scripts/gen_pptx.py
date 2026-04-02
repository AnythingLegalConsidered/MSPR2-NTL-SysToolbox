"""Generate the MSPR soutenance PPTX — clean corporate design."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# --- Palette: 2 couleurs + gris ---
NAVY = RGBColor(0x2B, 0x3A, 0x67)
ORANGE = RGBColor(0xE8, 0x83, 0x3A)
TEXT_DARK = RGBColor(0x33, 0x33, 0x3B)
TEXT_MID = RGBColor(0x6B, 0x70, 0x80)
TEXT_LIGHT = RGBColor(0x9B, 0x9F, 0xAA)
BG_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG_LIGHT = RGBColor(0xF5, 0xF6, 0xF8)
BG_CARD = RGBColor(0xEE, 0xEF, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN_OK = RGBColor(0x2D, 0x8A, 0x56)
RED_KO = RGBColor(0xC0, 0x39, 0x2B)


def set_slide_bg(slide, color=BG_WHITE):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text(slide, left, top, width, height, text, font_size=18, color=TEXT_DARK,
             bold=False, alignment=PP_ALIGN.LEFT, font_name="Segoe UI"):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_multiline(slide, left, top, width, height, lines, font_size=16, font_name="Segoe UI"):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(lines):
        if len(item) == 3:
            text, color, bold = item
        else:
            text, color = item
            bold = False
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.bold = bold
        p.font.name = font_name
        p.space_after = Pt(4)
    return txBox


def add_image(slide, path, left, top, width=None, height=None):
    kwargs = {}
    if width:
        kwargs["width"] = Inches(width)
    if height:
        kwargs["height"] = Inches(height)
    slide.shapes.add_picture(path, Inches(left), Inches(top), **kwargs)


def add_rect(slide, left, top, width, height, color=BG_CARD):
    shape = slide.shapes.add_shape(
        1, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_line(slide, left, top, width, color=NAVY, thickness=2.5):
    shape = slide.shapes.add_shape(
        1, Inches(left), Inches(top), Inches(width), Pt(thickness)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def slide_header(slide, title, subtitle=None):
    """Standard slide header: title + thin line + optional subtitle."""
    add_text(slide, 0.8, 0.4, 10, 0.8, title, 36, NAVY, bold=True)
    add_line(slide, 0.8, 1.1, 1.8, ORANGE)
    if subtitle:
        add_text(slide, 0.8, 1.2, 11, 0.4, subtitle, 15, TEXT_LIGHT)


# ============================================================
# SLIDE 1 — TITRE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
# Navy band left
add_rect(slide, 0, 0, 0.35, 7.5, NAVY)
add_line(slide, 1.2, 3.0, 2.5, ORANGE, 4)
add_text(slide, 1.2, 1.8, 10, 1, "NTL-SysToolbox", 52, NAVY, bold=True)
add_text(slide, 1.2, 3.2, 10, 0.8, "Outil CLI d'administration système", 24, TEXT_MID)
add_text(slide, 1.2, 3.8, 10, 0.5, "pour NordTransit Logistics", 24, TEXT_MID)
add_multiline(slide, 1.2, 5.2, 10, 1.0, [
    ("Ianis (Lead)  ·  Blaise  ·  Ojvind  ·  Zaid", TEXT_DARK, True),
    ("MSPR TPRE511 — EPSI — 2026", TEXT_LIGHT, False),
], font_size=18)


# ============================================================
# SLIDE 2 — CONTEXTE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Contexte — NordTransit Logistics",
             "Une PME logistique dont l'activité repose entièrement sur son SI")

items = [
    ("PME logistique, Hauts-de-France", "Siège à Lille + 3 entrepôts : Lens, Valenciennes, Arras"),
    ("~240 employés", "Jusqu'à 300 en haute saison avec intérim"),
    ("Le WMS est le cœur de métier", "Son arrêt stoppe les opérations sur les 4 sites (5h30 - 18h30)"),
    ("Équipe IT réduite : 4 personnes", "1 responsable, 1 admin sys/réseau, 1 technicien, 1 alternant"),
    ("Maintenance nocturne uniquement", "Fenêtres d'intervention très courtes, zéro coupure en journée"),
]
for i, (title, desc) in enumerate(items):
    y = 1.7 + i * 1.05
    if i % 2 == 0:
        add_rect(slide, 0.8, y, 11.7, 0.9, BG_LIGHT)
    add_text(slide, 1.1, y + 0.08, 5, 0.4, title, 17, NAVY, bold=True)
    add_text(slide, 1.1, y + 0.48, 11, 0.4, desc, 15, TEXT_MID)


# ============================================================
# SLIDE 3 — PROBLEMATIQUE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Problématique",
             "3 angles morts identifiés dans le SI de NordTransit Logistics")

cols = [
    ("Supervision", RED_KO, [
        "Surtout technique (ping, disque)",
        "Pas orientée service metier",
        "AD, DNS, MySQL non surveillés",
    ], "Module Diagnostic"),
    ("Sauvegardes", ORANGE, [
        "Scripts + NAS, jamais testées",
        "Pas d'objectif RPO / RTO",
        "Aucune verification d'intégrité",
    ], "Module Backup"),
    ("Obsolescence", NAVY, [
        "Aucun inventaire EOL",
        "OS en fin de vie non identifiés",
        "Risque de faille non maîtrisé",
    ], "Module Audit"),
]
for i, (title, color, bullets, solution) in enumerate(cols):
    x = 0.8 + i * 4.1
    add_rect(slide, x, 1.7, 3.8, 4.8, BG_LIGHT)
    add_line(slide, x + 0.3, 2.0, 1.5, color, 3)
    add_text(slide, x + 0.3, 2.15, 3.2, 0.5, title, 22, color, bold=True)
    for j, item in enumerate(bullets):
        add_text(slide, x + 0.3, 3.0 + j * 0.7, 3.2, 0.6, "·  " + item, 15, TEXT_MID)
    # Solution
    add_rect(slide, x + 0.3, 5.4, 3.2, 0.55, NAVY)
    add_text(slide, x + 0.4, 5.45, 3, 0.45, "→  " + solution, 14, WHITE, bold=True)


# ============================================================
# SLIDE 4 — NOTRE SOLUTION
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Notre solution",
             "Un outil unique couvrant les 3 besoins, conçu pour s'intégrer a la supervision existante")

features = [
    ("CLI Python interactif", "Menu lisible, utilisable sans formation"),
    ("3 modules indépendants", "Diagnostic  ·  Backup  ·  Audit"),
    ("Sorties JSON horodatées", "Format structuré exploitable en supervision"),
    ("Codes retour 0 - 3", "Compatible Nagios / Zabbix  (OK / WARNING / CRITICAL / UNKNOWN)"),
    ("Config YAML + secrets .env", "Séparation code / config, zéro secret en dur"),
    ("Cross-platform", "Fonctionne sur Windows et Linux"),
]
for i, (feat, desc) in enumerate(features):
    y = 1.7 + i * 0.85
    add_text(slide, 1.0, y, 5, 0.4, feat, 17, NAVY, bold=True)
    add_text(slide, 1.0, y + 0.35, 5, 0.4, desc, 14, TEXT_MID)

add_image(slide, "output/menu_principal.png", 7.0, 1.7, width=5.5)


# ============================================================
# SLIDE 5 — ARCHITECTURE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Architecture",
             "Chaque module est indépendant mais partage le meme contrat de sortie JSON")

# Diagram
add_rect(slide, 0.8, 1.6, 5.2, 5.2, BG_LIGHT)
arch = [
    ("  Utilisateur (terminal)", TEXT_LIGHT, False),
    ("         |", TEXT_LIGHT, False),
    ("    main.py (menu)", NAVY, True),
    ("         |", TEXT_LIGHT, False),
    ("  +------+------+------+", TEXT_LIGHT, False),
    ("  |      |      |      |", TEXT_LIGHT, False),
    ("Diag.  Backup  Audit", ORANGE, True),
    ("  |      |      |      |", TEXT_LIGHT, False),
    ("  +------+------+------+", TEXT_LIGHT, False),
    ("         |", TEXT_LIGHT, False),
    ("  build_result() -> JSON", GREEN_OK, True),
    ("         |", TEXT_LIGHT, False),
    ("  +------+------+", TEXT_LIGHT, False),
    ("  |             |", TEXT_LIGHT, False),
    ("Terminal   output/logs/", TEXT_DARK, False),
    ("(rich)     *.json", TEXT_MID, False),
]
add_multiline(slide, 1.2, 1.8, 4.5, 5, arch, font_size=14, font_name="Consolas")

# Contract
add_rect(slide, 6.5, 1.6, 6.2, 5.2, BG_LIGHT)
add_text(slide, 6.8, 1.75, 5, 0.5, "Contrat JSON uniforme", 20, NAVY, bold=True)
add_line(slide, 6.8, 2.2, 1.2, ORANGE, 2)
fields = [
    ("module", "diagnostic | backup | audit"),
    ("function", "nom de la fonction appelée"),
    ("timestamp", "date/heure ISO 8601 UTC"),
    ("status", "OK | WARNING | CRITICAL | UNKNOWN"),
    ("exit_code", "0 | 1 | 2 | 3"),
    ("target", "IP, hostname, base de données..."),
    ("details", "données spécifiques au check"),
    ("message", "texte lisible par un humain"),
]
for i, (key, val) in enumerate(fields):
    y = 2.5 + i * 0.4
    add_text(slide, 6.9, y, 1.5, 0.35, key, 13, NAVY, bold=True, font_name="Consolas")
    add_text(slide, 8.5, y, 4, 0.35, val, 13, TEXT_MID)

add_text(slide, 6.9, 5.8, 5, 0.35, "Seuils WARNING :  CPU / RAM / Disk > 80%", 14, ORANGE, bold=True)
add_text(slide, 6.9, 6.2, 5, 0.35, "Timeout par défaut :  10 secondes", 14, TEXT_MID)


# ============================================================
# SLIDE 6 — MODULE DIAGNOSTIC
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Module Diagnostic",
             "Les services critiques du siège sont-ils opérationnels ?")
add_text(slide, 11.0, 0.5, 2, 0.4, "Blaise", 18, ORANGE, bold=True, alignment=PP_ALIGN.RIGHT)

funcs = [
    ("check_ad_dns", "DC01", "Ports LDAP / DNS / Kerberos + résolution DNS"),
    ("check_mysql", "WMS-DB", "Port 3306 + version MySQL (sans authentification)"),
    ("check_linux", "Tout serveur", "Scan multi-ports, catégorisation des services actifs"),
    ("check_http", "Tout serveur web", "Status HTTP, header Server, temps de réponse"),
]
# Header
add_rect(slide, 0.8, 1.6, 5.8, 0.42, NAVY)
add_text(slide, 0.9, 1.62, 1.8, 0.35, "Fonction", 13, WHITE, bold=True)
add_text(slide, 2.7, 1.62, 1.3, 0.35, "Cible", 13, WHITE, bold=True)
add_text(slide, 3.9, 1.62, 3, 0.35, "Vérification", 13, WHITE, bold=True)

for i, (fn, target, desc) in enumerate(funcs):
    y = 2.1 + i * 0.5
    if i % 2 == 0:
        add_rect(slide, 0.8, y, 5.8, 0.45, BG_LIGHT)
    add_text(slide, 0.9, y + 0.05, 1.8, 0.35, fn, 12, NAVY, bold=True, font_name="Consolas")
    add_text(slide, 2.7, y + 0.05, 1.2, 0.35, target, 12, TEXT_MID)
    add_text(slide, 3.9, y + 0.05, 3, 0.35, desc, 12, TEXT_DARK)

add_image(slide, "output/menu_diagnostic.png", 0.8, 4.3, width=5.5)
add_image(slide, "output/result_diagnostic.png", 7.0, 1.6, width=5.8)


# ============================================================
# SLIDE 7 — MODULE BACKUP
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Module Backup",
             "Sauvegarder la base WMS de manière fiable et traçable")
add_text(slide, 11.0, 0.5, 2, 0.4, "Ojvind", 18, ORANGE, bold=True, alignment=PP_ALIGN.RIGHT)

# Functions
add_rect(slide, 0.8, 1.6, 5.8, 2.5, BG_LIGHT)
backup_info = [
    ("backup_database", NAVY, True),
    ("  Dump SQL via mysqldump (local ou SSH en fallback)", TEXT_MID, False),
    ("  → output/backups/wms_YYYYMMDD_HHMMSS.sql", TEXT_LIGHT, False),
    ("", TEXT_MID, False),
    ("export_table_csv", NAVY, True),
    ("  Export d'une table MySQL en CSV horodaté", TEXT_MID, False),
    ("  → output/exports/table_YYYYMMDD_HHMMSS.csv", TEXT_LIGHT, False),
]
add_multiline(slide, 1.0, 1.7, 5.4, 2.3, backup_info, font_size=14, font_name="Consolas")

# Security
add_rect(slide, 0.8, 4.4, 5.8, 2.6, BG_LIGHT)
add_text(slide, 1.0, 4.5, 5, 0.4, "Mesures de sécurité", 18, NAVY, bold=True)
add_line(slide, 1.0, 4.9, 1.2, ORANGE, 2)
sec_items = [
    "Mot de passe transmis via variable d'environnement (MYSQL_PWD)",
    "Validation du nom de table par regex — protection injection SQL",
    "Protection path traversal — pas de .. autorisé",
    "Fallback SSH automatique si mysqldump absent localement",
]
for i, item in enumerate(sec_items):
    add_text(slide, 1.2, 5.1 + i * 0.42, 5.2, 0.4, "·  " + item, 13, TEXT_MID)

add_image(slide, "output/result_backup.png", 7.0, 1.6, width=5.8)


# ============================================================
# SLIDE 8 — MODULE AUDIT
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Module Audit",
             "Quels equipements du parc sont obsolètes et représentent un risque ?")
add_text(slide, 11.0, 0.5, 2, 0.4, "Zaid", 18, ORANGE, bold=True, alignment=PP_ALIGN.RIGHT)

# Pipeline
add_rect(slide, 0.8, 1.6, 11.7, 0.7, BG_LIGHT)
add_text(slide, 1.0, 1.65, 11.5, 0.35,
         "scan_network  →  list_os_eol  →  audit_from_csv  →  generate_report",
         16, NAVY, bold=True, font_name="Consolas")
add_text(slide, 1.0, 1.98, 11.5, 0.3,
         "     (nmap)             (JSON local)        (croisement)            (rapport trié)",
         12, TEXT_LIGHT, font_name="Consolas")

# Table
funcs_audit = [
    ("scan_network", "Plage IP (CIDR)", "Machines détectées + ports + OS"),
    ("list_os_eol", "Base JSON locale", "Dates de fin de support par OS"),
    ("audit_from_csv", "Inventaire CSV", "Croisement inventaire x dates EOL"),
    ("generate_report", "Résultats combinés", "Rapport JSON + tableau coloré"),
]
add_rect(slide, 0.8, 2.5, 5.8, 0.42, NAVY)
add_text(slide, 0.9, 2.52, 1.8, 0.35, "Fonction", 13, WHITE, bold=True)
add_text(slide, 2.7, 2.52, 1.8, 0.35, "Entree", 13, WHITE, bold=True)
add_text(slide, 4.3, 2.52, 3, 0.35, "Sortie", 13, WHITE, bold=True)

for i, (fn, inp, out) in enumerate(funcs_audit):
    y = 3.0 + i * 0.48
    if i % 2 == 0:
        add_rect(slide, 0.8, y, 5.8, 0.43, BG_LIGHT)
    add_text(slide, 0.9, y + 0.05, 1.8, 0.35, fn, 12, NAVY, bold=True, font_name="Consolas")
    add_text(slide, 2.7, y + 0.05, 1.6, 0.35, inp, 12, TEXT_MID)
    add_text(slide, 4.3, y + 0.05, 3, 0.35, out, 12, TEXT_DARK)

add_image(slide, "output/menu_audit.png", 0.8, 5.2, width=5.0)
add_image(slide, "output/result_audit.png", 7.0, 2.5, width=5.8)


# ============================================================
# SLIDE 9 — LAB & CI/CD
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Lab de test & CI/CD",
             "Tester en conditions réelles et garantir la qualité à chaque commit")

# Lab
add_rect(slide, 0.8, 1.6, 5.8, 4.5, BG_LIGHT)
add_text(slide, 1.0, 1.7, 5, 0.4, "Lab Proxmox", 20, NAVY, bold=True)
add_line(slide, 1.0, 2.1, 1.0, ORANGE, 2)

lab_vms = [
    ("DC01", "Windows Server", "AD / DNS", "192.168.10.10"),
    ("WMS-DB", "Ubuntu 20.04", "Base MySQL (WMS)", "192.168.10.21"),
    ("WMS-APP", "Ubuntu 20.04", "Application WMS", "192.168.10.22"),
    ("SRV-OLD", "Win Server 2012 R2", "Legacy (test EOL)", "192.168.10.12"),
    ("SRV-LEGACY", "Ubuntu 18.04", "Legacy (test EOL)", "192.168.10.18"),
]
# Table header
add_rect(slide, 1.0, 2.3, 5.4, 0.38, NAVY)
cols_x = [1.1, 2.3, 3.65, 5.0]
for j, h in enumerate(["VM", "OS", "Role", "IP"]):
    add_text(slide, cols_x[j], 2.32, 1.2, 0.3, h, 11, WHITE, bold=True)

for i, (vm, os_name, role, ip) in enumerate(lab_vms):
    y = 2.72 + i * 0.4
    if i % 2 == 0:
        add_rect(slide, 1.0, y, 5.4, 0.36, BG_CARD)
    vals = [vm, os_name, role, ip]
    for j, v in enumerate(vals):
        c = NAVY if j == 0 else TEXT_MID
        add_text(slide, cols_x[j], y + 0.03, 1.3, 0.3, v, 11, c, bold=(j == 0))

add_text(slide, 1.0, 5.0, 5.4, 0.7,
         "Environnement reproduisant l'infra réelle de NTL pour valider chaque module avant merge.",
         13, TEXT_LIGHT)

# CI
add_rect(slide, 7.0, 1.6, 5.8, 4.5, BG_LIGHT)
add_text(slide, 7.2, 1.7, 5, 0.4, "CI/CD — GitHub Actions", 20, NAVY, bold=True)
add_line(slide, 7.2, 2.1, 1.0, ORANGE, 2)

ci_items = [
    ("Déclenchement", ORANGE, True),
    ("push : master, feature/*", TEXT_MID, False),
    ("pull_request : master", TEXT_MID, False),
    ("", TEXT_MID, False),
    ("Job 1 — Qualite du code", NAVY, True),
    ("ruff check src/ tests/  (lint)", TEXT_MID, False),
    ("mypy src/  (types)", TEXT_MID, False),
    ("", TEXT_MID, False),
    ("Job 2 — Tests (matrice)", NAVY, True),
    ("pytest --cov  (min 50%)", TEXT_MID, False),
    ("Python 3.10 / 3.11 / 3.12", TEXT_MID, False),
    ("", TEXT_MID, False),
    ("2 jobs en parallèle", ORANGE, True),
    ("Feedback en moins de 2 minutes", TEXT_MID, False),
]
add_multiline(slide, 7.3, 2.3, 5, 3.5, ci_items, font_size=13, font_name="Consolas")


# ============================================================
# SLIDE 10 — DEMO
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Demo live",
             "Scénario complet : diagnostic, sauvegarde, audit — chacun présente son module")

steps = [
    ("1", "Lancement du menu", "python src/main.py", "Ianis"),
    ("2", "Diagnostic AD/DNS", "Vérifier que le DC01 répond", "Blaise"),
    ("3", "Backup base WMS", "Sauvegarder la base wms en dump SQL", "Ojvind"),
    ("4", "Audit EOL", "Lister les OS en fin de vie", "Zaid"),
    ("5", "Résultats JSON", "Montrer les fichiers générés dans output/logs/", "Ianis"),
]
for i, (num, desc, cmd, who) in enumerate(steps):
    y = 1.7 + i * 1.05
    if i % 2 == 0:
        add_rect(slide, 0.8, y, 11.7, 0.9, BG_LIGHT)
    # Number circle
    circle = slide.shapes.add_shape(
        9,  # OVAL
        Inches(1.0), Inches(y + 0.15), Inches(0.55), Inches(0.55)
    )
    circle.fill.solid()
    circle.fill.fore_color.rgb = NAVY
    circle.line.fill.background()
    add_text(slide, 1.05, y + 0.17, 0.5, 0.5, num, 22, WHITE, bold=True, alignment=PP_ALIGN.CENTER)

    add_text(slide, 1.8, y + 0.1, 3.5, 0.4, desc, 19, TEXT_DARK, bold=True)
    add_text(slide, 1.8, y + 0.5, 6, 0.35, cmd, 14, TEXT_LIGHT)
    add_text(slide, 10.5, y + 0.2, 2, 0.4, who, 17, ORANGE, bold=True, alignment=PP_ALIGN.RIGHT)


# ============================================================
# SLIDE 11 — DOCUMENTATION
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Documentation",
             "Tout ce qu'il faut pour déployer et utiliser l'outil sans assistance")

# Livrables
add_rect(slide, 0.8, 1.6, 5.8, 3.5, BG_LIGHT)
add_text(slide, 1.0, 1.7, 5, 0.4, "Livrables", 20, NAVY, bold=True)
add_line(slide, 1.0, 2.1, 1.0, ORANGE, 2)
livrables = [
    "Dossier technique et fonctionnel",
    "Guide d'installation (setup en 5 commandes)",
    "10 docs numérotées (getting-started → lab-infra)",
    "Cheatsheet 1 page pour l'équipe",
    "Rapport CI/CD",
    "Execution de référence de l'audit d'obsolescence",
]
for i, item in enumerate(livrables):
    add_text(slide, 1.2, 2.3 + i * 0.4, 5.2, 0.35, "✓  " + item, 14, TEXT_DARK)

# Key point
add_rect(slide, 0.8, 5.4, 5.8, 1.3, NAVY)
add_multiline(slide, 1.0, 5.5, 5.4, 1.1, [
    ("La DSI peut déployer et utiliser", WHITE, True),
    ("l'outil sans assistance", WHITE, True),
    ("Documentation versionnée avec le code dans le repo Git", RGBColor(0xBA, 0xC2, 0xDE), False),
], font_size=15)

# Doc tree
add_rect(slide, 7.0, 1.6, 5.8, 5.1, BG_LIGHT)
add_text(slide, 7.2, 1.7, 5, 0.4, "docs/", 18, NAVY, bold=True, font_name="Consolas")
doc_items = [
    ("00-index", "Table des matières"),
    ("01-getting-started", "Installation"),
    ("02-team-guide", "Guide équipe"),
    ("03-module-logic", "Logique des modules"),
    ("04-interfaces", "Contrat JSON"),
    ("05-config", "Configuration"),
    ("06-utils", "Utilitaires"),
    ("07-cli", "Menu main.py"),
    ("08-ci-guide", "Guide CI/CD"),
    ("09-ci-report", "Rapport CI"),
    ("10-lab-infra", "Infrastructure lab"),
    ("cheatsheet", "Aide-mémoire"),
]
for i, (name, desc) in enumerate(doc_items):
    y = 2.2 + i * 0.37
    add_text(slide, 7.4, y, 2.2, 0.3, name, 12, NAVY, font_name="Consolas")
    add_text(slide, 9.6, y, 3, 0.3, desc, 12, TEXT_MID)


# ============================================================
# SLIDE 12 — DIFFICULTES
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Difficultes & compromis",
             "Chaque compromis a ete discuté en équipe et assumé en connaissance de cause")

diffs = [
    ("Portabilité Windows / Linux", "Python + libs cross-platform, tests CI sur Ubuntu"),
    ("Accès WinRM optionnel", "Fallback gracieux — fonctionne sans, mais signale le manque"),
    ("Base EOL locale vs API externe", "JSON local = pas de dépendance réseau, mais maintenance manuelle"),
    ("4 devs, 19h, modules liés", "Contrat JSON commun défini en amont → developpement parallèle"),
    ("Sécurité des credentials", "Variables d'env + .env, zéro secret dans le code ou les logs"),
]
# Header
add_rect(slide, 0.8, 1.6, 11.7, 0.45, NAVY)
add_text(slide, 1.0, 1.62, 4.5, 0.4, "Difficulte", 15, WHITE, bold=True)
add_text(slide, 5.5, 1.62, 7, 0.4, "Notre approche", 15, WHITE, bold=True)

for i, (diff, approach) in enumerate(diffs):
    y = 2.15 + i * 0.9
    if i % 2 == 0:
        add_rect(slide, 0.8, y, 11.7, 0.8, BG_LIGHT)
    add_text(slide, 1.0, y + 0.15, 4.3, 0.5, diff, 16, ORANGE, bold=True)
    add_text(slide, 5.5, y + 0.15, 7, 0.5, approach, 15, TEXT_DARK)


# ============================================================
# SLIDE 13 — BILAN
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Bilan & perspectives",
             "L'outil répond au cahier des charges et l'architecture permet d'aller plus loin")

# Done
add_rect(slide, 0.8, 1.6, 5.8, 4.8, BG_LIGHT)
add_text(slide, 1.0, 1.7, 5, 0.4, "Objectifs atteints", 20, GREEN_OK, bold=True)
add_line(slide, 1.0, 2.1, 1.0, GREEN_OK, 2)
done = [
    "3 modules fonctionnels et indépendants",
    "Menu CLI interactif avec Rich",
    "Sorties JSON horodatées + codes retour",
    "Configuration YAML + gestion des secrets",
    "CI/CD : lint + types + tests x 3 versions Python",
    "Documentation complète (10 docs + cheatsheet)",
    "Lab de test Proxmox reproduisant l'infra NTL",
]
for i, item in enumerate(done):
    add_text(slide, 1.2, 2.3 + i * 0.48, 5.2, 0.4, "✓  " + item, 15, TEXT_DARK)

# Perspectives
add_rect(slide, 7.0, 1.6, 5.8, 4.8, BG_LIGHT)
add_text(slide, 7.2, 1.7, 5, 0.4, "Perspectives", 20, NAVY, bold=True)
add_line(slide, 7.2, 2.1, 1.0, ORANGE, 2)
persp = [
    ("Intégration Zabbix / supervision", "Les codes retour sont déjà compatibles"),
    ("Backup planifié", "Cron ou Task Scheduler pour automatiser"),
    ("Base EOL dynamique", "API endoflife.date pour mise à jour auto"),
    ("Extension multi-sites", "Couvrir WH1, WH2, WH3 via les VPN existants"),
    ("Dashboard web", "Interface de visualisation des resultats"),
]
for i, (feat, desc) in enumerate(persp):
    y = 2.3 + i * 0.85
    add_text(slide, 7.4, y, 5, 0.4, "→  " + feat, 15, NAVY, bold=True)
    add_text(slide, 7.7, y + 0.38, 5, 0.35, desc, 13, TEXT_MID)


# ============================================================
# SLIDE 14 — QUESTIONS
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_rect(slide, 0, 0, 0.35, 7.5, NAVY)
add_line(slide, 1.2, 3.6, 2.5, ORANGE, 4)
add_text(slide, 1.2, 2.2, 11, 1, "Merci pour votre attention", 44, NAVY, bold=True)
add_text(slide, 1.2, 3.8, 11, 0.6, "Nous sommes prêts pour vos questions.", 22, TEXT_MID)
add_text(slide, 1.2, 5.2, 11, 0.5, "NTL-SysToolbox  —  Ianis  ·  Blaise  ·  Ojvind  ·  Zaid", 18, TEXT_LIGHT)


# ============================================================
output_path = "output/NTL-SysToolbox_Soutenance_v4.pptx"
prs.save(output_path)
print(f"PPTX saved: {output_path} ({os.path.getsize(output_path) // 1024} Ko)")
