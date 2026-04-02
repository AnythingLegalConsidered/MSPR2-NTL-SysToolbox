"""Generate terminal-style screenshots — Windows Terminal style."""
from PIL import Image, ImageDraw, ImageFont
import os


def render_terminal(lines, title, output_path, width=700, bg="#0c0c0c", fg="#cccccc"):
    try:
        font = ImageFont.truetype("consola.ttf", 15)
        title_font = ImageFont.truetype("segoeui.ttf", 13)
        tab_font = ImageFont.truetype("segoeui.ttf", 12)
    except Exception:
        font = ImageFont.load_default(size=15)
        title_font = font
        tab_font = font

    line_height = 21
    padding = 16
    title_bar_h = 32
    tab_bar_h = 28
    total_top = title_bar_h + tab_bar_h
    h = total_top + padding * 2 + line_height * len(lines) + 8
    corner = 10

    img = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Window background with rounded top
    draw.rounded_rectangle([(0, 0), (width - 1, h - 1)], radius=corner, fill=bg)

    # Title bar (dark gray, Windows style)
    title_bar_color = "#1f1f1f"
    draw.rounded_rectangle([(0, 0), (width - 1, title_bar_h + corner)],
                           radius=corner, fill=title_bar_color)
    draw.rectangle([(0, title_bar_h), (width - 1, title_bar_h + corner)],
                   fill=title_bar_color)

    # Window controls (right side, Windows style: _ [] X)
    ctrl_y = 10
    ctrl_color = "#999999"
    # Minimize
    draw.line([(width - 138, ctrl_y + 6), (width - 126, ctrl_y + 6)], fill=ctrl_color, width=1)
    # Maximize (square)
    draw.rectangle([(width - 98, ctrl_y + 2), (width - 86, ctrl_y + 12)], outline=ctrl_color, width=1)
    # Close X
    draw.line([(width - 58, ctrl_y + 2), (width - 46, ctrl_y + 12)], fill="#c42b1c", width=2)
    draw.line([(width - 58, ctrl_y + 12), (width - 46, ctrl_y + 2)], fill="#c42b1c", width=2)

    # Title text center
    draw.text((width // 2 - 80, 8), title, fill="#aaaaaa", font=title_font)

    # Tab bar
    tab_bar_color = "#181818"
    draw.rectangle([(0, title_bar_h), (width - 1, title_bar_h + tab_bar_h)], fill=tab_bar_color)
    # Active tab
    tab_w = 180
    draw.rounded_rectangle([(8, title_bar_h + 4), (8 + tab_w, title_bar_h + tab_bar_h)],
                           radius=6, fill=bg)
    # Tab icon (PS or terminal icon placeholder ">_")
    draw.text((18, title_bar_h + 8), ">_", fill="#5599ff", font=tab_font)
    draw.text((42, title_bar_h + 8), "Windows PowerShell", fill="#cccccc", font=tab_font)

    # Content
    y = total_top + padding
    for line in lines:
        if isinstance(line, tuple):
            text, color = line
        else:
            text, color = line, fg
        draw.text((padding, y), text, fill=color, font=font)
        y += line_height

    # Convert to RGB for saving
    final = Image.new("RGB", img.size, bg)
    final.paste(img, mask=img.split()[3])
    final.save(output_path)


# --- Menu Principal ---
render_terminal([
    ("", "#cccccc"),
    ("      NTL-SysToolbox", "#61afef"),
    ("  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510", "#555555"),
    ("  \u2502  1    Diagnostic          \u2502", "#cccccc"),
    ("  \u2502  2    Backup              \u2502", "#cccccc"),
    ("  \u2502  3    Audit               \u2502", "#cccccc"),
    ("  \u2502  0    Quitter             \u2502", "#777777"),
    ("  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518", "#555555"),
    ("", "#cccccc"),
    ("  Choix : _", "#61afef"),
], "NTL-SysToolbox \u2014 Menu Principal", "output/menu_principal.png")

# --- Diagnostic ---
render_terminal([
    ("", "#cccccc"),
    ("      Diagnostic", "#61afef"),
    ("  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510", "#555555"),
    ("  \u2502  1    V\u00e9rifier AD/DNS (DC01)                   \u2502", "#cccccc"),
    ("  \u2502  2    V\u00e9rifier MySQL (port + version)          \u2502", "#cccccc"),
    ("  \u2502  3    V\u00e9rifier services Linux (multi-ports)    \u2502", "#cccccc"),
    ("  \u2502  4    V\u00e9rifier HTTP/HTTPS                      \u2502", "#cccccc"),
    ("  \u2502  0    Retour                                   \u2502", "#777777"),
    ("  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518", "#555555"),
    ("", "#cccccc"),
    ("  Choix : 1", "#61afef"),
    ("  IP du DC (d\u00e9faut: dc01) :", "#61afef"),
], "NTL-SysToolbox \u2014 Diagnostic", "output/menu_diagnostic.png")

# --- Backup ---
render_terminal([
    ("", "#cccccc"),
    ("      Backup", "#61afef"),
    ("  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510", "#555555"),
    ("  \u2502  1    Backup base de donn\u00e9es (dump SQL)    \u2502", "#cccccc"),
    ("  \u2502  2    Export table en CSV                  \u2502", "#cccccc"),
    ("  \u2502  0    Retour                               \u2502", "#777777"),
    ("  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518", "#555555"),
    ("", "#cccccc"),
    ("  Choix : _", "#61afef"),
], "NTL-SysToolbox \u2014 Backup", "output/menu_backup.png")

# --- Audit ---
render_terminal([
    ("", "#cccccc"),
    ("      Audit", "#61afef"),
    ("  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510", "#555555"),
    ("  \u2502  1    Scanner le r\u00e9seau                    \u2502", "#cccccc"),
    ("  \u2502  2    Lister les dates EOL                 \u2502", "#cccccc"),
    ("  \u2502  3    Auditer depuis un CSV                \u2502", "#cccccc"),
    ("  \u2502  4    G\u00e9n\u00e9rer le rapport complet           \u2502", "#cccccc"),
    ("  \u2502  0    Retour                               \u2502", "#777777"),
    ("  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518", "#555555"),
    ("", "#cccccc"),
    ("  Choix : _", "#61afef"),
], "NTL-SysToolbox \u2014 Audit", "output/menu_audit.png")

# --- Result Diagnostic OK ---
render_terminal([
    ("", "#cccccc"),
    ("  Status: OK    exit_code: 0", "#98c379"),
    ("", "#cccccc"),
    ("  {", "#cccccc"),
    ('    "module": "diagnostic",', "#e5c07b"),
    ('    "function": "check_ad_dns",', "#e5c07b"),
    ('    "timestamp": "2026-04-02T14:30:00Z",', "#e5c07b"),
    ('    "status": "OK",', "#98c379"),
    ('    "exit_code": 0,', "#98c379"),
    ('    "target": "192.168.10.10",', "#e5c07b"),
    ('    "details": {', "#cccccc"),
    ('      "dns": true, "ldap": true,', "#98c379"),
    ('      "ports": {"53": true, "88": true, "389": true}', "#98c379"),
    ("    },", "#cccccc"),
    ('    "message": "AD et DNS op\u00e9rationnels sur DC01"', "#98c379"),
    ("  }", "#cccccc"),
], "R\u00e9sultat \u2014 check_ad_dns (OK)", "output/result_diagnostic.png", width=650)

# --- Result Backup OK ---
render_terminal([
    ("", "#cccccc"),
    ("  Status: OK    exit_code: 0", "#98c379"),
    ("", "#cccccc"),
    ("  {", "#cccccc"),
    ('    "module": "backup",', "#e5c07b"),
    ('    "function": "backup_database",', "#e5c07b"),
    ('    "timestamp": "2026-04-02T14:32:00Z",', "#e5c07b"),
    ('    "status": "OK",', "#98c379"),
    ('    "exit_code": 0,', "#98c379"),
    ('    "target": "wms",', "#e5c07b"),
    ('    "details": {', "#cccccc"),
    ('      "dump_path": "output/backups/wms_20260402.sql",', "#61afef"),
    ('      "size_bytes": 245760,', "#d19a66"),
    ('      "duration_seconds": 3.2', "#d19a66"),
    ("    },", "#cccccc"),
    ('    "message": "Backup de wms r\u00e9ussie (240 Ko)"', "#98c379"),
    ("  }", "#cccccc"),
], "R\u00e9sultat \u2014 backup_database (OK)", "output/result_backup.png", width=650)

# --- Result Audit WARNING ---
render_terminal([
    ("", "#cccccc"),
    ("  Status: WARNING    exit_code: 1", "#e5c07b"),
    ("", "#cccccc"),
    ("  {", "#cccccc"),
    ('    "module": "audit",', "#e5c07b"),
    ('    "function": "list_os_eol",', "#e5c07b"),
    ('    "status": "WARNING",  "exit_code": 1,', "#e5c07b"),
    ('    "details": {', "#cccccc"),
    ('      "total": 6, "eol_count": 2,', "#d19a66"),
    ('      "entries": [', "#cccccc"),
    ('        {"os":"Win Server 2008 R2", "status":"EXPIRED", "days":-2270}', "#e06c75"),
    ('        {"os":"Windows 7",          "status":"EXPIRED", "days":-2270}', "#e06c75"),
    ('        {"os":"Win Server 2012 R2", "status":"SOON",    "days": 194}', "#e5c07b"),
    ('        {"os":"Ubuntu 18.04",       "status":"OK",      "days": 730}', "#98c379"),
    ('        {"os":"Win Server 2022",    "status":"OK",      "days":2021}', "#98c379"),
    ('        {"os":"Ubuntu 20.04",       "status":"OK",      "days":1461}', "#98c379"),
    ("      ]", "#cccccc"),
    ("    },", "#cccccc"),
    ('    "message": "2 OS en fin de vie d\u00e9tect\u00e9s sur 6"', "#e5c07b"),
    ("  }", "#cccccc"),
], "R\u00e9sultat \u2014 list_os_eol (WARNING)", "output/result_audit.png", width=750)

for f in ["menu_principal", "menu_diagnostic", "menu_backup", "menu_audit",
          "result_diagnostic", "result_backup", "result_audit"]:
    p = f"output/{f}.png"
    print(f"{p} - {os.path.getsize(p) // 1024} Ko")
print("OK all screenshots")
