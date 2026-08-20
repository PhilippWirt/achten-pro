#!/usr/bin/env python3
"""Deterministically build the four public DE/EN pages from two templates."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
TEMPLATES = SOURCE / "templates"
LOCALES = SOURCE / "locales"
SHARED = SOURCE / "shared"

TEMPLATE_BY_SITE = {
    "achten-pro": TEMPLATES / "achten-pro.html",
    "playfight": TEMPLATES / "playfight.html",
}


def translate_text_nodes(document: str, mapping: dict[str, str]) -> tuple[str, set[str]]:
    """Translate text nodes only; never touch CSS or JavaScript bodies."""
    parts = re.split(r"(<[^>]+>)", document)
    blocked: list[str] = []
    used: set[str] = set()
    for index, part in enumerate(parts):
        if part.startswith("<"):
            match = re.match(r"</?\s*([a-zA-Z0-9-]+)", part)
            if match:
                tag = match.group(1).lower()
                if part.startswith("</"):
                    if blocked and blocked[-1] == tag:
                        blocked.pop()
                elif tag in {"style", "script"} and not part.rstrip().endswith("/>"):
                    blocked.append(tag)
            continue
        if blocked or not part.strip():
            continue
        normalized = " ".join(html.unescape(part).split())
        if normalized in mapping:
            prefix = part[: len(part) - len(part.lstrip())]
            suffix = part[len(part.rstrip()) :]
            parts[index] = prefix + mapping[normalized] + suffix
            used.add(normalized)
    return "".join(parts), used


def translate_attributes(document: str, mappings: dict[str, dict[str, str]]) -> str:
    for attribute, values in mappings.items():
        for source, target in sorted(values.items(), key=lambda item: len(item[0]), reverse=True):
            pattern = re.compile(
                rf"(\b{re.escape(attribute)}\s*=\s*)([\"']){re.escape(source)}\2"
            )
            document = pattern.sub(
                lambda match: match.group(1) + match.group(2) + target + match.group(2),
                document,
            )
    return document


def language_switch(config: dict) -> str:
    partial = (SHARED / "language-switch.html").read_text()
    current = config["lang"]
    values = {
        "SITE_KEY": config["site"],
        "LANGUAGE_LABEL": "Sprache wählen" if current == "de" else "Choose language",
        "DE_URL": config["de_url"],
        "EN_URL": config["en_url"],
        "DE_PRESSED": "true" if current == "de" else "false",
        "EN_PRESSED": "true" if current == "en" else "false",
        "DE_CURRENT": ' aria-current="page"' if current == "de" else "",
        "EN_CURRENT": ' aria-current="page"' if current == "en" else "",
        "DE_CLASS": " active" if current == "de" else " inactive",
        "EN_CLASS": " active" if current == "en" else " inactive",
        "CURRENT_LANGUAGE_HINT": "Aktuelle Sprache: Deutsch" if current == "de" else "Current language: English",
    }
    for key, value in values.items():
        partial = partial.replace("{{" + key + "}}", value)
    return partial.rstrip()


def set_metadata(document: str, config: dict) -> str:
    document = re.sub(
        r"<html\b[^>]*>",
        f'<html lang="{config["lang"]}">',
        document,
        count=1,
    )
    document = re.sub(r"<link\s+rel=[\"']alternate[\"'][^>]*>\s*", "", document)
    document = re.sub(r"<link\s+rel=[\"']canonical[\"'][^>]*>\s*", "", document)
    alternates = (
        f'  <link rel="alternate" hreflang="de" href="https://achten.pro{config["de_url"]}">\n'
        f'  <link rel="alternate" hreflang="en" href="https://achten.pro{config["en_url"]}">\n'
        f'  <link rel="alternate" hreflang="x-default" href="{config["canonical"]}">\n'
        f'  <link rel="canonical" href="{config["canonical"]}">\n'
    )
    viewport = re.compile(r"(<meta\s+name=[\"']viewport[\"'][^>]*>\s*)", re.I)
    document, count = viewport.subn(r"\1\n" + alternates, document, count=1)
    if count != 1:
        raise RuntimeError("viewport metadata anchor missing")
    document = re.sub(
        r"<title>.*?</title>",
        f'<title>{html.escape(config["title"])}</title>',
        document,
        count=1,
        flags=re.S,
    )
    description = html.escape(config["description"], quote=True)
    document, count = re.subn(
        r"<meta\s+name=[\"']description[\"'][^>]*>",
        f'<meta name="description" content="{description}">',
        document,
        count=1,
        flags=re.S | re.I,
    )
    if count != 1:
        raise RuntimeError("description metadata missing")
    return document


def build(config_path: Path) -> tuple[Path, int, int]:
    config = json.loads(config_path.read_text())
    template = TEMPLATE_BY_SITE[config["site"]].read_text(errors="strict")

    document, used = translate_text_nodes(template, config.get("text", {}))
    document = translate_attributes(document, config.get("attributes", {}))

    for source, target in config.get("path_replacements", {}).items():
        document = document.replace(source, target)

    switch_pattern = re.compile(
        r'<button\b(?=[^>]*\bclass="lang-switch")[\s\S]*?</button>', re.I
    )
    document, count = switch_pattern.subn(language_switch(config), document, count=1)
    if count != 1:
        raise RuntimeError(f"language switch missing in {config_path.name}")

    document = set_metadata(document, config)
    shared_css = (SHARED / "styles.css").read_text().rstrip()
    shared_js = (SHARED / "language-switch.js").read_text().rstrip()
    document = document.replace("</style>", f"\n\n    /* Shared language switch */\n{shared_css}\n  </style>", 1)
    document = document.replace("</body>", f"  <script>\n{shared_js}\n  </script>\n</body>", 1)
    document = document.replace(
        "<!DOCTYPE html>",
        "<!DOCTYPE html>\n<!-- Generated by build.py. Edit source/templates and source/locales, not this file. -->",
        1,
    )
    document = "\n".join(line.rstrip() for line in document.splitlines()) + "\n"

    output = ROOT / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, newline="\n")
    return output, len(used), len(config.get("text", {}))


def main() -> None:
    outputs = []
    for locale in sorted(LOCALES.glob("*.json")):
        output, used, total = build(locale)
        outputs.append(output)
        print(f"built {output.relative_to(ROOT)} ({used}/{total} locale entries used)")

    legacy = ROOT / "playfight" / "en"
    if legacy.is_file():
        legacy.unlink()
        print("removed obsolete file playfight/en")

    expected = {
        ROOT / "index.html",
        ROOT / "en" / "index.html",
        ROOT / "playfight" / "index.html",
        ROOT / "playfight" / "de" / "index.html",
    }
    if set(outputs) != expected:
        raise RuntimeError("locale outputs do not match the four-page architecture")


if __name__ == "__main__":
    main()
