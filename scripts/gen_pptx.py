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
TEXT_MID = RGBColor(0x7A, 0x7F, 0x90)
TEXT_LIGHT = RGBColor(0xB0, 0xB4, 0xBE)
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
        "Pas orientée service métier",
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
             "Un outil unique couvrant les 3 besoins, conçu pour s'intégrer à la supervision existante")

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

add_image(slide, "output/screenshots/menu_principal.png", 7.0, 1.7, width=5.5)


# ============================================================
# SLIDE 5 — ORGANISATION EQUIPE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Organisation de l'équipe",
             "4 développeurs, 19 heures, un contrat commun")

# Tableau rôles
add_rect(slide, 0.8, 1.6, 11.7, 0.45, NAVY)
for j, h in enumerate(["Membre", "Rôle", "Périmètre"]):
    add_text(slide, [1.0, 3.0, 8.0][j], 1.62, 3, 0.4, h, 15, WHITE, bold=True)

team = [
    ("Ianis", "Lead, archi, CI/CD, intégration", "Framework + CLI + reviews"),
    ("Blaise", "Développeur module", "Module Diagnostic"),
    ("Ojvind", "Développeur module", "Module Backup"),
    ("Zaid", "Développeur module", "Module Audit"),
]
for i, (name, role, scope) in enumerate(team):
    y = 2.15 + i * 0.6
    if i % 2 == 0:
        add_rect(slide, 0.8, y, 11.7, 0.55, BG_LIGHT)
    add_text(slide, 1.0, y + 0.1, 1.8, 0.4, name, 16, NAVY, bold=True)
    add_text(slide, 3.0, y + 0.1, 4.8, 0.4, role, 14, TEXT_MID)
    add_text(slide, 8.0, y + 0.1, 4.3, 0.4, scope, 14, TEXT_DARK)

# Méthode de travail
add_rect(slide, 0.8, 4.6, 5.5, 2.6, BG_LIGHT)
add_text(slide, 1.0, 4.7, 5, 0.4, "Méthode de travail", 18, NAVY, bold=True)
add_line(slide, 1.0, 5.1, 1.0, ORANGE, 2)
method_items = [
    "Contrat JSON défini ensemble en amont (interfaces.py)",
    "1 branche par module (feature/module-*)",
    "Pull requests + code review par le Lead",
    "CI automatique à chaque push",
    "Merge squash sur master",
]
for i, item in enumerate(method_items):
    add_text(slide, 1.2, 5.3 + i * 0.35, 4.8, 0.3, "·  " + item, 13, TEXT_MID)

# Encart workflow visuel
add_rect(slide, 6.8, 4.6, 5.7, 2.6, BG_LIGHT)
add_text(slide, 7.0, 4.7, 5, 0.4, "Workflow Git", 18, NAVY, bold=True)
add_line(slide, 7.0, 5.1, 1.0, ORANGE, 2)
workflow = [
    ("1.", "Chaque dev code sur sa branche feature/*", TEXT_MID),
    ("2.", "Push → CI vérifie (lint + types + tests)", TEXT_MID),
    ("3.", "Pull request → review par le Lead", TEXT_MID),
    ("4.", "Merge squash → master propre", TEXT_MID),
]
for i, (num, desc, color) in enumerate(workflow):
    add_text(slide, 7.2, 5.3 + i * 0.4, 0.4, 0.35, num, 14, ORANGE, bold=True)
    add_text(slide, 7.6, 5.3 + i * 0.4, 4.5, 0.35, desc, 13, color)


# ============================================================
# SLIDE 6 — ARCHITECTURE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Architecture",
             "Chaque module est indépendant mais partage le même contrat de sortie JSON")

# Diagram — formes PowerPoint
add_rect(slide, 0.8, 1.6, 5.2, 5.6, BG_LIGHT)

# main.py (top)
add_rect(slide, 1.8, 1.9, 3.2, 0.6, NAVY)
add_text(slide, 1.8, 1.95, 3.2, 0.5, "main.py (menu CLI)", 15, WHITE, bold=True,
         alignment=PP_ALIGN.CENTER)

# Flèche main → modules
add_line(slide, 3.4, 2.55, 0.01, TEXT_LIGHT, 2)
add_rect(slide, 3.35, 2.55, 0.1, 0.4, TEXT_LIGHT)  # trait vertical

# 3 modules (milieu)
DIAG_COLOR = RGBColor(0xE8, 0x83, 0x3A)   # orange
BACKUP_COLOR = RGBColor(0x2D, 0x8A, 0x56)  # vert
AUDIT_COLOR = RGBColor(0x6C, 0x5C, 0xE7)   # violet

modules = [
    ("Diagnostic", DIAG_COLOR, 1.1),
    ("Backup", BACKUP_COLOR, 2.65),
    ("Audit", AUDIT_COLOR, 4.2),
]
for name, color, x in modules:
    add_rect(slide, x, 3.1, 1.4, 0.6, color)
    add_text(slide, x, 3.15, 1.4, 0.5, name, 13, WHITE, bold=True,
             alignment=PP_ALIGN.CENTER)

# Flèches modules → build_result
add_rect(slide, 3.35, 3.75, 0.1, 0.35, TEXT_LIGHT)  # trait vertical

# build_result() (bas)
add_rect(slide, 1.8, 4.2, 3.2, 0.6, GREEN_OK)
add_text(slide, 1.8, 4.25, 3.2, 0.5, "build_result() → JSON", 14, WHITE, bold=True,
         alignment=PP_ALIGN.CENTER)

# Sorties
add_rect(slide, 3.35, 4.85, 0.1, 0.3, TEXT_LIGHT)  # trait vertical

out_items = [
    ("Terminal (Rich)", 1.3, TEXT_DARK),
    ("output/logs/*.json", 3.5, TEXT_DARK),
]
for label, x, color in out_items:
    add_rect(slide, x, 5.25, 2.0, 0.5, BG_CARD)
    add_text(slide, x, 5.3, 2.0, 0.4, label, 12, color, alignment=PP_ALIGN.CENTER)

# Légende
add_text(slide, 1.0, 6.1, 4.8, 0.3,
         "Point d'entrée → 3 modules indépendants → format JSON uniforme",
         11, TEXT_LIGHT)

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

add_image(slide, "output/screenshots/menu_diagnostic.png", 0.8, 4.3, width=5.5)
add_image(slide, "output/screenshots/result_diagnostic.png", 7.0, 1.6, width=5.8)


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
    ("  Dump SQL mysqldump (local ou SSH)", TEXT_MID, False),
    ("  → output/backups/wms_*.sql", TEXT_LIGHT, False),
    ("", TEXT_MID, False),
    ("export_table_csv", NAVY, True),
    ("  Export table MySQL en CSV horodaté", TEXT_MID, False),
    ("  → output/exports/table_*.csv", TEXT_LIGHT, False),
]
add_multiline(slide, 1.0, 1.7, 5.4, 2.3, backup_info, font_size=13, font_name="Consolas")

# Security
add_rect(slide, 0.8, 4.4, 5.8, 2.6, BG_LIGHT)
add_text(slide, 1.0, 4.5, 5, 0.4, "Mesures de sécurité", 18, NAVY, bold=True)
add_line(slide, 1.0, 4.9, 1.2, ORANGE, 2)
sec_items = [
    "Mot de passe via variable d'env (MYSQL_PWD)",
    "Validation nom de table par regex (anti-injection)",
    "Protection path traversal (pas de .. autorisé)",
    "Fallback SSH si mysqldump absent localement",
]
for i, item in enumerate(sec_items):
    add_text(slide, 1.2, 5.1 + i * 0.42, 5.2, 0.4, "·  " + item, 13, TEXT_MID)

add_image(slide, "output/screenshots/result_backup.png", 7.0, 1.6, width=5.8)


# ============================================================
# SLIDE 8 — MODULE AUDIT
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Module Audit",
             "Quels équipements du parc sont obsolètes et représentent un risque ?")
add_text(slide, 11.0, 0.5, 2, 0.4, "Zaid", 18, ORANGE, bold=True, alignment=PP_ALIGN.RIGHT)

# Pipeline
add_rect(slide, 0.8, 1.6, 11.7, 0.7, BG_LIGHT)
add_text(slide, 1.0, 1.65, 11.5, 0.35,
         "scan_network → list_os_eol → audit_from_csv → generate_report",
         14, NAVY, bold=True, font_name="Consolas")
add_text(slide, 1.0, 1.98, 11.5, 0.3,
         "   (nmap)          (JSON local)      (croisement)         (rapport trié)",
         11, TEXT_LIGHT, font_name="Consolas")

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

add_image(slide, "output/screenshots/menu_audit.png", 0.8, 5.2, width=5.0)
add_image(slide, "output/screenshots/result_audit_1.png", 7.0, 2.5, width=5.8)


# ============================================================
# SLIDE 10 — LAB PROXMOX
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Environnement de test",
             "Un lab qui reproduit l'infra réelle de NTL pour valider chaque module")

# Tableau VMs (pleine largeur)
lab_vms = [
    ("DC01", "Win Server 2022", "AD / DNS", ".10"),
    ("WMS-DB", "Ubuntu 20.04", "Base MySQL (WMS)", ".21"),
    ("WMS-APP", "Ubuntu 20.04", "Application WMS", ".22"),
    ("SRV-OLD", "Win Server 2012 R2", "Legacy (test EOL)", ".12"),
    ("SRV-LEGACY", "Ubuntu 18.04", "Legacy (test EOL)", ".18"),
]
# Table header
add_rect(slide, 0.8, 1.6, 11.7, 0.45, NAVY)
lab_cols_x = [1.0, 3.5, 6.5, 9.5]
lab_cols_w = [2.4, 3.0, 3.0, 2.5]
for j, h in enumerate(["VM", "OS", "Rôle", "192.168.10.x"]):
    add_text(slide, lab_cols_x[j], 1.62, lab_cols_w[j], 0.4, h, 15, WHITE, bold=True)

for i, (vm, os_name, role, ip) in enumerate(lab_vms):
    y = 2.15 + i * 0.55
    if i % 2 == 0:
        add_rect(slide, 0.8, y, 11.7, 0.5, BG_LIGHT)
    vals = [vm, os_name, role, ip]
    for j, v in enumerate(vals):
        c = NAVY if j == 0 else TEXT_MID
        add_text(slide, lab_cols_x[j], y + 0.08, lab_cols_w[j], 0.35, v, 14, c,
                 bold=(j == 0))

# Explication
add_rect(slide, 0.8, 5.1, 5.5, 2.0, BG_LIGHT)
add_text(slide, 1.0, 5.2, 5, 0.4, "Pourquoi un lab ?", 18, NAVY, bold=True)
add_line(slide, 1.0, 5.6, 1.0, ORANGE, 2)
why_lab = [
    "Tester en conditions réelles sans toucher à la production",
    "Chaque module validé sur des VMs identiques à l'infra NTL",
    "VMs legacy pour tester la détection EOL",
]
for i, item in enumerate(why_lab):
    add_text(slide, 1.2, 5.8 + i * 0.35, 4.8, 0.3, "·  " + item, 13, TEXT_MID)

# Hébergement
add_rect(slide, 6.8, 5.1, 5.7, 2.0, NAVY)
add_multiline(slide, 7.0, 5.3, 5.2, 1.6, [
    ("Hébergé sur Proxmox VE", WHITE, True),
    ("Hyperviseur open source", RGBColor(0xBA, 0xC2, 0xDE), False),
    ("", WHITE, False),
    ("Réseau : 192.168.10.0/24 (switch virtuel)", RGBColor(0xBA, 0xC2, 0xDE), False),
    ("5 VMs, déployées via scripts post-install", RGBColor(0xBA, 0xC2, 0xDE), False),
], font_size=14)


# ============================================================
# SLIDE 11 — CI/CD GITHUB ACTIONS
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
slide_header(slide, "Intégration continue",
             "Chaque commit est vérifié automatiquement en moins de 2 minutes")

# Pipeline en formes
add_text(slide, 0.8, 1.5, 11, 0.4, "Pipeline GitHub Actions", 18, NAVY, bold=True)

# Trigger
add_rect(slide, 0.8, 2.0, 3.5, 0.8, BG_LIGHT)
add_text(slide, 1.0, 2.05, 3, 0.35, "Déclenchement", 14, ORANGE, bold=True)
add_text(slide, 1.0, 2.4, 3, 0.3, "push / PR sur master ou feature/*", 12, TEXT_MID)

# Flèche
add_rect(slide, 4.35, 2.3, 0.5, 0.08, TEXT_LIGHT)

# Job 1
add_rect(slide, 4.9, 2.0, 3.5, 0.8, NAVY)
add_text(slide, 5.1, 2.05, 3, 0.35, "Job 1 — Qualité", 14, WHITE, bold=True)
add_text(slide, 5.1, 2.4, 3, 0.3, "ruff check + mypy src/", 12, RGBColor(0xBA, 0xC2, 0xDE))

# Job 2
add_rect(slide, 4.9, 3.0, 3.5, 0.8, NAVY)
add_text(slide, 5.1, 3.05, 3, 0.35, "Job 2 — Tests", 14, WHITE, bold=True)
add_text(slide, 5.1, 3.4, 3, 0.3, "pytest --cov × Python 3.10/3.11/3.12", 12,
         RGBColor(0xBA, 0xC2, 0xDE))

# Parallèle label
add_text(slide, 8.6, 2.5, 2, 0.5, "En parallèle", 13, ORANGE, bold=True)

# Flèche vers merge
add_rect(slide, 6.6, 3.85, 0.08, 0.3, TEXT_LIGHT)

# Merge OK
add_rect(slide, 5.5, 4.2, 2.3, 0.6, GREEN_OK)
add_text(slide, 5.5, 4.25, 2.3, 0.5, "✓  Merge OK", 16, WHITE, bold=True,
         alignment=PP_ALIGN.CENTER)

# Détails en bas
add_rect(slide, 0.8, 5.2, 11.7, 1.8, BG_LIGHT)
ci_details = [
    ("Lint", "ruff check src/ tests/ — style + erreurs", TEXT_MID),
    ("Types", "mypy src/ — vérification statique des types", TEXT_MID),
    ("Tests", "pytest avec couverture, matrice 3 versions Python", TEXT_MID),
    ("Feedback", "Résultat en moins de 2 minutes par run", ORANGE),
]
for i, (label, desc, color) in enumerate(ci_details):
    y = 5.35 + i * 0.38
    add_text(slide, 1.0, y, 1.5, 0.3, label, 14, NAVY, bold=True)
    add_text(slide, 2.5, y, 9.5, 0.3, desc, 13, color)


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
             "Chaque compromis a été discuté en équipe et assumé en connaissance de cause")

diffs = [
    ("Portabilité Windows / Linux", "Python + libs cross-platform, tests CI sur Ubuntu"),
    ("Accès WinRM optionnel", "Fallback gracieux — fonctionne sans, mais signale le manque"),
    ("Base EOL locale vs API externe", "JSON local = pas de dépendance réseau, mais maintenance manuelle"),
    ("4 devs, 19h, modules liés", "Contrat JSON commun défini en amont → développement parallèle"),
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
    ("Dashboard web", "Interface de visualisation des résultats"),
]
for i, (feat, desc) in enumerate(persp):
    y = 2.3 + i * 0.85
    add_text(slide, 7.4, y, 5, 0.4, "→  " + feat, 15, NAVY, bold=True)
    add_text(slide, 7.7, y + 0.38, 5, 0.35, desc, 13, TEXT_MID)

# Encart métriques projet
add_rect(slide, 0.8, 6.6, 11.7, 0.7, NAVY)
add_text(slide, 1.0, 6.65, 11.5, 0.3,
         "62 commits  ·  110 tests  ·  ~2 500 lignes Python  ·  10 docs  ·  5 VMs lab",
         14, WHITE, bold=True, alignment=PP_ALIGN.CENTER)
add_text(slide, 1.0, 6.95, 11.5, 0.3,
         "CI : ruff + mypy + pytest × 3 versions Python",
         12, RGBColor(0xBA, 0xC2, 0xDE), alignment=PP_ALIGN.CENTER)


# ============================================================
# SLIDE 16 — QUESTIONS
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_rect(slide, 0, 0, 0.35, 7.5, NAVY)
add_line(slide, 1.2, 3.6, 2.5, ORANGE, 4)
add_text(slide, 1.2, 2.2, 11, 1, "Merci pour votre attention", 44, NAVY, bold=True)
add_text(slide, 1.2, 3.8, 11, 0.6, "Nous sommes prêts pour vos questions.", 22, TEXT_MID)
add_text(slide, 1.2, 5.2, 11, 0.5, "NTL-SysToolbox  —  Ianis  ·  Blaise  ·  Ojvind  ·  Zaid", 18, TEXT_LIGHT)


# ============================================================
output_path = "output/NTL-SysToolbox_Soutenance_v6.pptx"
prs.save(output_path)
print(f"PPTX saved: {output_path} ({os.path.getsize(output_path) // 1024} Ko)")
