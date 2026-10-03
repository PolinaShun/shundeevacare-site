#!/usr/bin/env python3
"""Проставляет/обновляет ?v=<hash> у локальной статики в HTML — обход кэша хостинга.

Зачем: .htaccess отдаёт text/css и application/javascript с `access plus 1 month`.
Если в ссылке нет версии, вернувшиеся посетители до месяца видят СТАРЫЙ файл:
правка доезжает до сервера, но не до их браузера (реальный случай 03.10.2026 —
мобильная правка в main.css не была видна тем, кто уже открывал сайт).

Порядок работы: правим файлы -> запускаем скрипт -> коммитим вместе.
Проверка без записи: python3 scripts/bust_cache.py --check  (код 1, если версии устарели).

Файлы в ASSETS версионируются по своему содержимому (md5, 8 символов),
поэтому хэш меняется ровно тогда, когда меняется файл.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ["styles/main.css"]


def digest(rel: str) -> str:
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()[:8]


def main() -> int:
    check = "--check" in sys.argv
    versions: dict[str, str] = {}
    for rel in ASSETS:
        if not (ROOT / rel).exists():
            print(f"нет файла: {rel}")
            return 2
        versions[rel] = digest(rel)

    changed: list[str] = []
    stale: list[str] = []
    for html in sorted(ROOT.rglob("*.html")):
        text = original = html.read_text(encoding="utf-8")
        for rel, ver in versions.items():
            name = Path(rel).name
            pattern = re.compile(r'(href|src)="([^"]*/)?' + re.escape(name) + r'(\?v=[0-9a-f]+)?"')

            def repl(match: re.Match[str], name: str = name, ver: str = ver) -> str:
                prefix = match.group(2) or ""
                return f'{match.group(1)}="{prefix}{name}?v={ver}"'

            text = pattern.sub(repl, text)
        if text != original:
            rel_path = str(html.relative_to(ROOT))
            if check:
                stale.append(rel_path)
            else:
                html.write_text(text, encoding="utf-8")
                changed.append(rel_path)

    if check:
        if stale:
            print("версии устарели в файлах:")
            for item in stale:
                print(f"  {item}")
            return 1
        print("версии актуальны")
        return 0

    for rel, ver in versions.items():
        print(f"{rel} -> ?v={ver}")
    print(f"обновлено файлов: {len(changed)}")
    for item in changed:
        print(f"  {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
