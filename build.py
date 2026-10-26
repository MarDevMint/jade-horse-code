#!/usr/bin/env python3
"""Build the Jade Horse Code-OSS extension (dark + light).

Renders Omarchy's own VS Code template with each palette, then layers the
surfaces the way the Omarchy theme does (sidebar/bars one step darker than the
editor, hairline borders, a visible line highlight) instead of one flat color.
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = Path("/usr/share/omarchy/default/themed/vscode-theme.json.tpl")
DARK_COLORS = HERE / "palettes/dark-colors.toml"
LIGHT_COLORS = HERE / "palettes/light-colors.toml"
EXT_ID = "mardevmint.jade-horse"
EXT_VERSION = "1.0.0"
EXT_BASE = Path.home() / ".vscode-oss/extensions"
EXT_DIR = Path(__file__).resolve().parent

THEMES = [
    ("Jade Horse", "jade-horse-dark.json", DARK_COLORS, "vs-dark"),
    ("Jade Horse Light", "jade-horse-light.json", LIGHT_COLORS, "vs"),
]


def palette(colors_file):
    out = subprocess.run(
        ["omarchy-theme-color", "--file", str(colors_file), "--all"],
        check=True, capture_output=True, text=True,
    ).stdout
    return dict(line.split("\t", 1) for line in out.splitlines() if "\t" in line)


def render(p):
    text = re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: p[m.group(1)], TEMPLATE.read_text())
    return json.loads(text)


def surfaces(p):
    dark = p["theme_type"] == "dark"
    bg, chrome, edge, raised = (
        p["background"], p["dark_background"], p["darker_background"], p["lighter_background"],
    )
    # Floating widgets lift off the editor: lighter in dark mode, paper-white in light
    widget = raised
    field = edge if dark else raised
    line = raised + ("90" if dark else "")
    if not dark:
        line = chrome

    return {
        "editor.background": bg,
        "editor.lineHighlightBackground": line,
        "editor.lineHighlightBorder": "#00000000",
        "editorGutter.background": bg,
        "editorLineNumber.foreground": p["muted"] + "b0",
        "editorLineNumber.activeForeground": p["dark_foreground"],
        "editorCursor.foreground": p["accent"],
        "editor.selectionBackground": p["selection"] + ("c0" if dark else ""),
        "editor.inactiveSelectionBackground": p["selection"] + "70",
        "editor.selectionHighlightBackground": p["selection"] + "60",
        "editor.wordHighlightBackground": p["selection"] + "50",
        "editorWhitespace.foreground": p["muted"] + "40",
        "editorRuler.foreground": edge,

        "activityBar.background": chrome,
        "activityBar.border": edge,
        "activityBar.foreground": p["accent"],
        "activityBar.inactiveForeground": p["muted"],
        "activityBar.activeBorder": p["accent"],
        "activityBarBadge.background": p["accent"],
        "activityBarBadge.foreground": bg,

        "sideBar.background": chrome,
        "sideBar.border": edge,
        "sideBarSectionHeader.background": chrome,
        "sideBarSectionHeader.border": edge,
        "sideBarTitle.foreground": p["dark_foreground"],

        "titleBar.activeBackground": chrome,
        "titleBar.inactiveBackground": chrome,
        "titleBar.activeForeground": p["dark_foreground"],
        "titleBar.inactiveForeground": p["muted"],
        "titleBar.border": edge,

        "statusBar.background": chrome,
        "statusBar.noFolderBackground": chrome,
        "statusBar.foreground": p["dark_foreground"],
        "statusBar.border": edge,
        "statusBarItem.remoteBackground": p["accent"],
        "statusBarItem.remoteForeground": bg,

        "editorGroupHeader.tabsBackground": chrome,
        "editorGroupHeader.tabsBorder": edge,
        "editorGroup.border": edge,
        "tab.activeBackground": bg,
        "tab.unfocusedActiveBackground": bg,
        "tab.inactiveBackground": chrome,
        "tab.activeForeground": p["foreground"],
        "tab.inactiveForeground": p["muted"],
        "tab.border": edge,
        "tab.activeBorder": bg,
        "tab.activeBorderTop": p["accent"],
        "tab.unfocusedActiveBorderTop": p["muted"],
        "breadcrumb.background": bg,

        "panel.background": chrome,
        "panel.border": edge,
        "panelTitle.activeBorder": p["accent"],
        "terminal.background": chrome,

        "editorWidget.background": widget,
        "editorWidget.border": edge,
        "editorHoverWidget.background": widget,
        "editorHoverWidget.border": edge,
        "editorSuggestWidget.background": widget,
        "editorSuggestWidget.border": edge,
        "editorSuggestWidget.selectedBackground": p["selection"],
        "quickInput.background": widget,
        "quickInputList.focusBackground": p["selection"],
        "menu.background": widget,
        "menu.border": edge,
        "menu.selectionBackground": p["selection"],
        "menu.selectionForeground": p["bright_foreground"],
        "notifications.background": widget,
        "notifications.border": edge,
        "notificationCenterHeader.background": chrome,

        "input.background": field,
        "input.border": edge,
        "dropdown.background": field,
        "dropdown.border": edge,
        "checkbox.background": field,
        "checkbox.border": edge,

        "list.activeSelectionBackground": p["selection"],
        "list.activeSelectionForeground": p["bright_foreground"],
        "list.inactiveSelectionBackground": p["selection"] + "80",
        "list.hoverBackground": p["selection"] + "50",
        "list.focusOutline": p["accent"] + "60",

        "scrollbarSlider.background": p["muted"] + "30",
        "scrollbarSlider.hoverBackground": p["muted"] + "50",
        "scrollbarSlider.activeBackground": p["muted"] + "70",
        "scrollbar.shadow": "#00000000",
        "widget.shadow": "#00000030" if dark else "#1f3b3218",
    }


def build():
    themes_dir = EXT_DIR / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)

    for label, filename, colors_file, _ in THEMES:
        p = palette(colors_file)
        theme = render(p)
        theme["name"] = label
        theme["colors"].update(surfaces(p))
        (themes_dir / filename).write_text(json.dumps(theme, indent=4) + "\n")

    package = {
        "name": "jade-horse",
        "displayName": "Jade Horse",
        "description": "Jade Horse for Code-OSS, dark and light, from the Omarchy theme palette",
        "publisher": "local",
        "version": EXT_VERSION,
        "engines": {"vscode": "^1.70.0"},
        "categories": ["Themes"],
        "contributes": {
            "themes": [
                {"label": label, "uiTheme": ui, "path": f"./themes/{filename}"}
                for label, filename, _, ui in THEMES
            ]
        },
    }
    (EXT_DIR / "package.json").write_text(json.dumps(package, indent=4) + "\n")



def register():
    # Code-OSS only loads extensions listed in extensions.json
    registry = EXT_BASE / "extensions.json"
    entries = json.loads(registry.read_text()) if registry.exists() else []
    entries = [e for e in entries if e.get("identifier", {}).get("id") != EXT_ID]
    entries.append({
        "identifier": {"id": EXT_ID},
        "version": EXT_VERSION,
        "location": {
            "$mid": 1, "fsPath": str(EXT_DIR), "external": f"file://{EXT_DIR}",
            "path": str(EXT_DIR), "scheme": "file",
        },
        "relativeLocation": EXT_DIR.name,
    })
    registry.write_text(json.dumps(entries))


if __name__ == "__main__":
    build()
