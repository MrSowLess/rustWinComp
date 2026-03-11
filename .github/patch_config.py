#!/usr/bin/env python3
"""
patch_config.py — вшивает host и key в исходники RustDesk перед сборкой.

Использование (из корня репо RustDesk):
    python patch_config.py

Или с параметрами:
    python patch_config.py --host myserver.example.com --key "ABC123="
"""

import re
import pathlib
import argparse
import sys

DEFAULT_HOST = "expamle.rustdesk.ru"
DEFAULT_KEY  = "123="

CONFIG_PATH  = pathlib.Path("libs/hbb_common/src/config.rs")


def patch(host: str, key: str) -> None:
    if not CONFIG_PATH.exists():
        print(f"[ОШИБКА] Файл не найден: {CONFIG_PATH}", file=sys.stderr)
        print("Запусти скрипт из корневой директории репозитория RustDesk.", file=sys.stderr)
        sys.exit(1)

    original = CONFIG_PATH.read_text(encoding="utf-8")
    patched  = original

    # ── Patch 1: RENDEZVOUS_SERVERS ──────────────────────────────────────
    pattern_servers = (
        r'(pub const RENDEZVOUS_SERVERS\s*:\s*&\[&str\]\s*=\s*&\[)[^\]]*(\])'
    )
    replacement_servers = rf'\g<1>"{host}"\2'
    patched, n1 = re.subn(pattern_servers, replacement_servers, patched)
    if n1 == 0:
        print("[ПРЕДУПРЕЖДЕНИЕ] RENDEZVOUS_SERVERS — паттерн не найден, пропускаем.")
    else:
        print(f"[OK] RENDEZVOUS_SERVERS → \"{host}\"")

    # ── Patch 2: RS_PUB_KEY ──────────────────────────────────────────────
    pattern_key = r'(pub const RS_PUB_KEY\s*:\s*&str\s*=\s*")[^"]*(")'
    replacement_key = rf'\g<1>{key}\g<2>'
    patched, n2 = re.subn(pattern_key, replacement_key, patched)
    if n2 == 0:
        print("[ПРЕДУПРЕЖДЕНИЕ] RS_PUB_KEY — паттерн не найден, пропускаем.")
    else:
        print(f"[OK] RS_PUB_KEY → \"{key}\"")

    if patched == original:
        print("[!] Файл не изменился — возможно, паттерны уже совпадают или формат изменился.")
        return

    CONFIG_PATH.write_text(patched, encoding="utf-8")
    print(f"\n[ГОТОВО] Патч записан в {CONFIG_PATH}")

    # Показываем затронутые строки
    print("\n─── Изменённые строки ───")
    for i, line in enumerate(patched.splitlines(), 1):
        if host in line or key in line:
            print(f"  {i:4d}: {line.rstrip()}")


def main():
    parser = argparse.ArgumentParser(description="Патч config.rs для RustDesk")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Адрес rendezvous-сервера")
    parser.add_argument("--key",  default=DEFAULT_KEY,  help="Публичный ключ (base64)")
    args = parser.parse_args()

    print(f"Host : {args.host}")
    print(f"Key  : {args.key}")
    print()
    patch(args.host, args.key)


if __name__ == "__main__":
    main()
