#!/usr/bin/env python3
"""Выкладка статического сайта на FTP хостинга — устойчивая версия.

Зачем этот скрипт вместо готовых FTP-экшенов:
  FTP-сервер хостинга периодически не присылает финальный ответ 226 после загрузки
  файла (и иногда «Timeout (control socket)»), из-за чего готовые экшены падают,
  хотя файл на самом деле залит. Здесь решение проверяется не по коду ответа,
  а по РАЗМЕРУ файла на сервере, с повторами.

Что делает:
  1) заливает файлы репозитория (без .git, архивов, служебных документов);
  2) после каждого файла сверяет его размер на сервере с локальным;
  3) при расхождении повторяет (до 3 попыток с паузой);
  4) падает с кодом 1, только если после повторов размеры не совпали.

Переменные окружения: FTP_SERVER, FTP_USERNAME, FTP_PASSWORD
(в workflow подставляются из секретов репозитория).
Локальный запуск: DRY_RUN=1 python3 scripts/ftp_deploy.py — только показать, что не сходится.
"""
import ftplib
import os
import sys
import time

SERVER = os.environ.get("FTP_SERVER", "185.127.24.17")
USER = os.environ.get("FTP_USERNAME", "")
PASSWORD = os.environ.get("FTP_PASSWORD", "")
REMOTE_ROOT = os.environ.get("FTP_REMOTE_ROOT", "/www/shundeevacare.ru")
DRY_RUN = os.environ.get("DRY_RUN") == "1"

SKIP_DIRS = {".git", ".github", "v2", "scripts", "бекапы проектов", "projects", ".claude", "node_modules", "__pycache__"}
SKIP_SUFFIX = (".zip", ".docx")
SKIP_NAMES = {"CLAUDE-CONTEXT.md", "MATERIALS-GUIDE.md", "INSTRUCTIONS.md", ".DS_Store",
              "CONTEXT.md", "AGENTS.md", ".cursorrules"}


def local_files():
    """Список файлов на выкладку. Приоритет — то, что лежит в git (в CI это и есть
    чекаут). Если git недоступен, идём по файловой системе с теми же исключениями.
    Так локальный запуск не пытается залить CONTEXT.md/AGENTS.md и прочее служебное."""
    import subprocess
    try:
        raw = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True, check=True).stdout
        files = []
        for rel in raw.split("\0"):
            rel = rel.strip()
            if not rel or rel.startswith(".git") or "/.git" in rel:
                continue
            if rel.split("/")[0] in SKIP_DIRS:
                continue
            if rel.endswith(SKIP_SUFFIX) or os.path.basename(rel) in SKIP_NAMES:
                continue
            files.append(rel)
        return sorted(files)
    except Exception:  # noqa: BLE001
        out = []
        for dirpath, dirnames, filenames in os.walk("."):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.startswith(".") and fn not in (".htaccess", ".gitignore"):
                    continue
                if fn.endswith(SKIP_SUFFIX) or fn in SKIP_NAMES:
                    continue
                rel = os.path.relpath(os.path.join(dirpath, fn), ".")
                out.append(rel.replace(os.sep, "/"))
        return sorted(out)


def connect():
    ftp = ftplib.FTP()
    ftp.connect(SERVER, 21, timeout=90)
    ftp.login(USER, PASSWORD)
    ftp.voidcmd("TYPE I")          # бинарный режим: без него SIZE отвечает «not allowed in ASCII mode»
    ftp.set_pasv(True)
    return ftp


def ensure_dir(ftp, path):
    try:
        ftp.cwd(path)
        ftp.cwd(REMOTE_ROOT)
        return
    except ftplib.all_errors:
        pass
    try:
        ftp.sendcmd("MKD " + path)
    except ftplib.all_errors:
        pass
    try:
        ftp.cwd(path)
        ftp.cwd(REMOTE_ROOT)
    except ftplib.all_errors:
        pass


def remote_size(ftp, rel):
    try:
        return ftp.size(f"{REMOTE_ROOT}/{rel}")
    except ftplib.all_errors:
        return None


def upload(ftp, rel, local_size, attempts=3):
    for attempt in range(1, attempts + 1):
        try:
            with open(rel, "rb") as fh:
                ftp.storbinary(f"STOR {REMOTE_ROOT}/{rel}", fh, blocksize=16384)
        except ftplib.all_errors as exc:
            print(f"    попытка {attempt}: ответ сервера не получен ({repr(exc)[:60]}) — проверяю размер")
        size = remote_size(ftp, rel)
        if size == local_size:
            return True, attempt
        time.sleep(3)
    return False, attempts


def main():
    if not USER or not PASSWORD:
        print("НЕТ FTP_USERNAME/FTP_PASSWORD — нечего делать")
        return 1
    files = local_files()
    print(f"файлов к выкладке: {len(files)}")
    try:
        ftp = connect()
    except Exception as exc:  # noqa: BLE001
        print(f"нет соединения с FTP: {exc}")
        return 1
    print("соединение установлено")

    dirs = sorted({os.path.dirname(f) for f in files if os.path.dirname(f)})
    for d in dirs:
        ensure_dir(ftp, f"{REMOTE_ROOT}/{d}")

    ok, retried, failed, skipped = 0, 0, [], 0
    for rel in files:
        local_size = os.path.getsize(rel)
        if DRY_RUN:
            cur = remote_size(ftp, rel)
            if cur != local_size:
                print(f"  расхождение: {rel} ({local_size} → на сервере {cur})")
                skipped += 1
            continue
        if remote_size(ftp, rel) == local_size:
            ok += 1
            continue
        good, attempts = upload(ftp, rel, local_size)
        if good:
            ok += 1
            if attempts > 1:
                retried += 1
        else:
            failed.append(rel)
            print(f"  НЕ УДАЛОСЬ: {rel} ({local_size} байт)")

    try:
        ftp.quit()
    except Exception:  # noqa: BLE001
        pass

    if DRY_RUN:
        print(f"режим проверки: расхождений {skipped} из {len(files)}")
        return 0
    print(f"в порядке: {ok}; понадобились повторы: {retried}; не удалось: {len(failed)}")
    for rel in failed:
        print("   ", rel)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
