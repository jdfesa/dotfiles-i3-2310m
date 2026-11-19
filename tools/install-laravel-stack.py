#!/usr/bin/python3
"""Review or install the optional native Debian 13 Laravel development stack."""
import argparse
import datetime
import json
import os
from pathlib import Path
import pwd
import re
import secrets
import signal
import shutil
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "config/laravel/mariadb.cnf": "/etc/mysql/mariadb.conf.d/90-laravel-local.cnf",
    "config/laravel/phpmyadmin.inc.php": "/etc/phpmyadmin/conf.d/90-laravel-local.php",
    "config/laravel/phpmyadmin.service": "/etc/systemd/system/laravel-phpmyadmin.service",
    "config/laravel/phpmyadmin-router.php": "/usr/local/share/bgh-laravel/phpmyadmin-router.php",
}
POLICY = Path("/usr/sbin/policy-rc.d")
POLICY_CONTENT = b"#!/bin/sh\n# Temporary guard for the reviewed Laravel package installation.\nexit 101\n"


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def packages():
    names = (ROOT / "config/laravel/packages-debian.txt").read_text().splitlines()
    if not names or any(not re.fullmatch(r"[a-z0-9][a-z0-9+.-]*", name) for name in names):
        raise ValueError("Invalid package inventory")
    return names


def regular_parents(path):
    for parent in path.parents:
        if parent.is_symlink():
            raise ValueError(f"Symlinked parent: {parent}")
    if path.is_symlink():
        raise ValueError(f"Symlinked target: {path}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Not a regular file: {path}")


def plan():
    run(["/usr/bin/apt-get", "-s", "--no-install-recommends", "--no-remove", "install", *packages()])
    for source, destination in FILES.items():
        regular_parents(Path(destination))
        print(f"Install root:root 644: {source} -> {destination}", flush=True)
    print("No boot activation. Preserve database root socket authentication.", flush=True)


def private_directory(path, uid, gid):
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError(f"Symlinked private directory: {parent}")
    if path.exists():
        info = path.stat()
        if not path.is_dir() or info.st_uid != uid or stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError(f"Expected an account-owned private directory: {path}")
    else:
        path.mkdir(mode=0o700)
        os.chown(path, uid, gid)


def create_database(account):
    directory = Path(account.pw_dir) / ".local/state/laravel-development"
    private_directory(directory, account.pw_uid, account.pw_gid)
    credentials = directory / "database.env"
    if credentials.is_symlink():
        raise ValueError("Refusing a credential symlink")
    if credentials.exists():
        info = credentials.stat()
        if not credentials.is_file() or info.st_uid != account.pw_uid or stat.S_IMODE(info.st_mode) != 0o600:
            raise ValueError("Unsafe existing credential file")
        print("Existing private database credentials preserved; no account changes.", flush=True)
        return
    query = ("SELECT COUNT(*) FROM mysql.user WHERE User='laravel';"
             "SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME='laravel';")
    counts = run(["/usr/bin/mariadb", "--batch", "--skip-column-names"],
                 input=query, text=True, capture_output=True).stdout.split()
    if counts != ["0", "0"]:
        raise ValueError("Existing laravel database/account found; preserve and review it manually")
    password = secrets.token_urlsafe(32)
    data = ("DB_CONNECTION=mysql\nDB_HOST=127.0.0.1\nDB_PORT=3306\n"
            f"DB_DATABASE=laravel\nDB_USERNAME=laravel\nDB_PASSWORD={password}\n")
    # Persist privately before SQL: even a partial database failure must not lose the password.
    fd = os.open(credentials, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as stream:
        os.fchown(stream.fileno(), account.pw_uid, account.pw_gid)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    sql = ("CREATE DATABASE `laravel` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
           f"CREATE USER 'laravel'@'127.0.0.1' IDENTIFIED BY '{password}';"
           "GRANT ALL PRIVILEGES ON `laravel`.* TO 'laravel'@'127.0.0.1';")
    # Password stays out of argv, shell history, stdout and Git.
    result = subprocess.run(["/usr/bin/mariadb", "--batch"], input=sql,
                            text=True, capture_output=True, check=False)
    if result.returncode:
        raise ValueError("Database setup failed; private credentials were retained for recovery")
    print(f"Development database created. Private credentials: {credentials}", flush=True)


def verify_database(account):
    credentials = Path(account.pw_dir) / ".local/state/laravel-development/database.env"
    code = '''
try {
    $c = parse_ini_file($argv[1], false, INI_SCANNER_RAW);
    if (($c['DB_USERNAME'] ?? '') !== 'laravel' || empty($c['DB_PASSWORD'])) { exit(1); }
    $pdo = new PDO('mysql:host=127.0.0.1;port=3306;dbname=laravel',
                   $c['DB_USERNAME'], $c['DB_PASSWORD']);
    if ((int) $pdo->query('SELECT 1')->fetchColumn() !== 1) { exit(1); }
    echo "Development database connection verified.\\n";
} catch (Throwable $e) {
    fwrite(STDERR, "Development database connection failed; inspect private credentials locally.\\n");
    exit(1);
}
'''
    run(["/usr/sbin/runuser", "-u", account.pw_name, "--", "/usr/bin/php8.4", "-r", code, str(credentials)])


def apply():
    if os.geteuid() != 0 or os.environ.get("SUDO_USER") != "jd":
        raise ValueError("Run --apply through authenticated sudo from the jd account")
    release = dict(line.split("=", 1) for line in Path("/etc/os-release").read_text().splitlines() if "=" in line)
    if release.get("ID", "").strip('"') != "debian" or release.get("VERSION_ID", "").strip('"') != "13":
        raise ValueError("This profile requires Debian 13")
    if POLICY.exists() or POLICY.is_symlink():
        raise ValueError("An existing policy-rc.d needs review; it will not be replaced")
    for unit in ("mariadb.service", "laravel-phpmyadmin.service"):
        state = subprocess.run(["/usr/bin/systemctl", "is-active", unit],
                               capture_output=True, text=True, check=False).stdout.strip()
        if state not in ("inactive", "failed", "unknown"):
            raise ValueError(f"Stop and review the existing {unit} before installation")
    for destination in FILES.values():
        regular_parents(Path(destination))
    account = pwd.getpwnam("jd")
    os.umask(0o077)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = Path("/var/backups") / ("bgh-laravel-" + stamp)
    backup.mkdir(mode=0o700)
    records = []
    for destination in FILES.values():
        path = Path(destination)
        item = {"destination": destination, "existed": path.exists()}
        if path.exists():
            item["mode"] = stat.S_IMODE(path.stat().st_mode)
            item["backup"] = str(len(records))
            shutil.copy2(path, backup / item["backup"])
            (backup / item["backup"]).chmod(0o600)
        records.append(item)
    (backup / "files.json").write_text(json.dumps(records, indent=2) + "\n")
    print(f"Private system rollback inventory: {backup}", flush=True)
    run(["/usr/bin/apt-get", "update"])
    plan()
    selections = ("phpmyadmin phpmyadmin/reconfigure-webserver multiselect\n"
                  "phpmyadmin phpmyadmin/dbconfig-install boolean false\n")
    run(["/usr/bin/debconf-set-selections"], input=selections, text=True)
    fd = os.open(POLICY, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o755)
    with os.fdopen(fd, "wb") as stream:
        stream.write(POLICY_CONTENT)
    POLICY.chmod(0o755)
    policy_inode = POLICY.stat().st_ino
    def interrupted(_signal, _frame):
        raise SystemExit("Installation interrupted; removing the temporary service-start guard")
    previous_handler = signal.signal(signal.SIGTERM, interrupted)
    try:
        run(["/usr/bin/apt-get", "--assume-yes", "--no-install-recommends", "--no-remove",
             "install", *packages()], env={**os.environ, "DEBIAN_FRONTEND": "noninteractive"})
    finally:
        signal.signal(signal.SIGTERM, previous_handler)
        if (not POLICY.is_symlink() and POLICY.exists() and POLICY.stat().st_ino == policy_inode
                and POLICY.read_bytes() == POLICY_CONTENT):
            POLICY.unlink()
        else:
            print("Temporary service-start policy changed; preserve and review it.", flush=True)
    for source, destination in FILES.items():
        target = Path(destination)
        regular_parents(target)
        if not target.parent.exists():
            target.parent.mkdir(mode=0o755, parents=True)
            target.parent.chmod(0o755)
        run(["/usr/bin/install", "-o", "root", "-g", "root", "-m", "644", str(ROOT / source), destination])
    run(["/usr/bin/php8.4", "-l", FILES["config/laravel/phpmyadmin.inc.php"]])
    run(["/usr/bin/php8.4", "-l", FILES["config/laravel/phpmyadmin-router.php"]])
    run(["/usr/bin/systemctl", "daemon-reload"])
    run(["/usr/bin/systemctl", "disable", "mariadb.service"])
    # Stop socket activation too if a future Debian package introduces it enabled.
    for unit in ("mariadb.socket", "mariadb-extra.socket"):
        loaded = subprocess.run(["/usr/bin/systemctl", "show", "--value", "--property=LoadState", unit],
                                capture_output=True, text=True, check=False).stdout.strip()
        if loaded == "loaded":
            run(["/usr/bin/systemctl", "disable", "--now", unit])
    try:
        run(["/usr/bin/systemctl", "start", "mariadb.service"])
        create_database(account)
        verify_database(account)
        run(["/usr/bin/systemctl", "start", "laravel-phpmyadmin.service"])
        run(["/usr/bin/mariadb", "--batch", "--skip-column-names", "-e",
             "SELECT VERSION(); SELECT @@bind_address;"])
        run(["/usr/bin/curl", "--fail", "--silent", "--retry", "6", "--retry-delay", "1",
             "--retry-connrefused", "--output", "/dev/null", "http://127.0.0.1:8080/"])
    finally:
        run(["/usr/bin/systemctl", "stop", "laravel-phpmyadmin.service", "mariadb.service"])
    print("Native Laravel stack installed. Both services are stopped and not enabled at boot.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Install with authenticated sudo; default is a read-only simulation")
    args = parser.parse_args()
    try:
        if args.apply:
            apply()
        else:
            plan()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Installation stopped: {error}\n")


if __name__ == "__main__":
    main()
