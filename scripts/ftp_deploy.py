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
  3) при сбое связи — ПЕРЕПОДКЛЮЧАЕТСЯ и повторяет (до 3 попыток на операцию);
  4) в конце делает сплошную проверку размеров всех файлов и перезаливает расхождения;
  5) падает с кодом 1, только если после повторов размеры не совпали.

Почему с переподключением: 04.10.2026 контрольное соединение с хостингом оборвалось
посреди выкладки. Скрипт ловил ошибку на каждом следующем файле и валил прогон,
оставив один файл залитым НАПОЛОВИНУ (blog.html 15928 из 17186 байт). Соединение
надо поднимать заново, а не продолжать по мёртвому сокету.

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
# AGENTS.md/CONTEXT.md — правила и доступы для агентов: живут в репозитории,
# на хостинг не выкладываются (правила для агентов не должны быть на публичном сайте).

ATTEMPTS = 3          # попыток на одну операцию (размер/загрузка)
SLEEP_BETWEEN = 3     # пауза между попытками, сек


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


class Deployer:
    """FTP с самовосстановлением: любая ошибка связи = переподключение и повтор."""

    def __init__(self):
        self.ftp = None
        self.dirs = []
        self.reconnects = 0
        self.dropped_errors = 0

    def connect(self):
        ftp = ftplib.FTP()
        ftp.connect(SERVER, 21, timeout=90)
        ftp.login(USER, PASSWORD)
        ftp.voidcmd("TYPE I")      # бинарный режим: без него SIZE отвечает «not allowed in ASCII mode»
        ftp.set_pasv(True)
        self.ftp = ftp
        self.reconnects += 1
        for d in self.dirs:
            self._ensure_dir(d)
        return ftp

    def drop(self):
        if self.ftp is not None:
            try:
                if getattr(self.ftp, "sock", None) is not None:
                    self.ftp.close()
            except Exception:  # noqa: BLE001
                pass
            self.ftp = None

    def _ensure_dir(self, path):
        ftp = self.ftp
        if ftp is None:
            return False
        for cmd in ("cwd", "mkd"):
            try:
                if cmd == "cwd":
                    ftp.cwd(path)
                else:
                    ftp.sendcmd("MKD " + path)
                ftp.cwd(REMOTE_ROOT)
                return True
            except ftplib.all_errors:
                continue
        return False

    def call(self, fn, label, attempts=ATTEMPTS):
        """Выполнить операцию с переподключением. Возвращает результат или None."""
        for attempt in range(1, attempts + 1):
            try:
                if self.ftp is None:
                    self.connect()
                return fn(self.ftp)
            except ftplib.all_errors as exc:
                self.dropped_errors += 1
                print(f"    {label}: сбой связи ({repr(exc)[:70]}) — переподключаюсь ({attempt}/{attempts})")
                self.drop()
                time.sleep(SLEEP_BETWEEN)
        return None

    def remote_size(self, rel):
        return self.call(lambda ftp: ftp.size(f"{REMOTE_ROOT}/{rel}"), f"SIZE {rel}")

    def upload(self, rel, local_size):
        def _store(ftp):
            with open(rel, "rb") as fh:
                ftp.storbinary(f"STOR {REMOTE_ROOT}/{rel}", fh, blocksize=16384)

        for attempt in range(1, ATTEMPTS + 1):
            self.call(_store, f"STOR {rel}")
            size = self.remote_size(rel)
            if size == local_size:
                return True, attempt
            time.sleep(SLEEP_BETWEEN)
        return False, ATTEMPTS

    def quit(self):
        try:
            if self.ftp is not None:
                self.ftp.quit()
        except Exception:  # noqa: BLE001
            pass
        self.ftp = None


def main():
    if not USER or not PASSWORD:
        print("НЕТ FTP_USERNAME/FTP_PASSWORD — нечего делать")
        return 1
    files = local_files()
    print(f"файлов к выкладке: {len(files)}")

    deployer = Deployer()
    deployer.dirs = sorted({f"{REMOTE_ROOT}/{os.path.dirname(f)}" for f in files if os.path.dirname(f)})
    if deployer.call(lambda ftp: ftp.cwd(REMOTE_ROOT), "подключение") is None:
        print("нет соединения с FTP")
        return 1
    print("соединение установлено")

    if DRY_RUN:
        mism = 0
        for rel in files:
            cur = deployer.remote_size(rel)
            if cur != os.path.getsize(rel):
                print(f"  расхождение: {rel} ({os.path.getsize(rel)} → на сервере {cur})")
                mism += 1
        deployer.quit()
        print(f"режим проверки: расхождений {mism} из {len(files)}")
        return 0

    ok, retried, failed = 0, 0, []
    for rel in files:
        local_size = os.path.getsize(rel)
        if deployer.remote_size(rel) == local_size:
            ok += 1
            continue
        good, attempts = deployer.upload(rel, local_size)
        if good:
            ok += 1
            if attempts > 1:
                retried += 1
        else:
            failed.append(rel)
            print(f"  НЕ УДАЛОСЬ: {rel} ({local_size} байт)")

    # Сплошная контрольная проверка: перезаливаем то, что всё ещё расходится.
    if failed:
        print(f"контрольная проверка: перезаливаю {len(failed)} файл(ов)")
        still = []
        for rel in failed:
            local_size = os.path.getsize(rel)
            good, _ = deployer.upload(rel, local_size)
            if good:
                ok += 1
                retried += 1
                print(f"  удалось со второй серии: {rel}")
            else:
                still.append(rel)
        failed = still

    deployer.quit()
    print(f"в порядке: {ok}; понадобились повторы: {retried}; переподключений: {deployer.reconnects}; не удалось: {len(failed)}")
    for rel in failed:
        print("   ", rel)
    if failed:
        print("ИТОГ: на сервере остались файлы неполного размера — сайт может отдавать обрезанные страницы")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
