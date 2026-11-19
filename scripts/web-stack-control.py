"""Fixed, non-GTK operations for the native local web stack."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SERVICES = {"apache2.service": "Apache / PHP", "mariadb.service": "MariaDB"}
PORTS = {"apache2.service": "80, 8080", "mariadb.service": "3306"}
LOGS = {"apache2.service": Path("/var/log/apache2/error.log"),
        "mariadb.service": Path("/var/log/mysql/error.log")}
CONFIGS = {
    "apache2.service": [Path("/etc/apache2/ports.conf"),
                        Path("/etc/apache2/conf-available/bgh-web-stack.conf"),
                        Path("/etc/phpmyadmin/conf.d/90-laravel-local.php")],
    "mariadb.service": [Path("/etc/mysql/mariadb.conf.d/90-laravel-local.cnf")],
}
URL = "http://127.0.0.1/phpmyadmin/"
SITE_URL = "http://127.0.0.1/"
WEB_ROOT = "/var/www/html"


def service_command(action, unit):
    if action not in ("start", "stop", "restart") or unit not in (*SERVICES, "all"):
        raise ValueError("Unsupported service action")
    targets = list(SERVICES) if unit == "all" else [unit]
    return ["/usr/bin/systemctl", "--no-ask-password", action, *targets]


def service_info():
    result = subprocess.run(
        ["/usr/bin/systemctl", "show", "--no-pager",
         "--property=Id,LoadState,ActiveState,MainPID", *SERVICES],
        capture_output=True, text=True, timeout=5, check=False)
    info = {unit: {"state": "Unavailable", "pid": "—"} for unit in SERVICES}
    for block in result.stdout.strip().split("\n\n"):
        fields = dict(line.split("=", 1) for line in block.splitlines() if "=" in line)
        unit = fields.get("Id")
        if unit in info:
            state = ("Not installed" if fields.get("LoadState") == "not-found"
                     else fields.get("ActiveState", "Unavailable"))
            info[unit] = {"state": state, "pid": fields.get("MainPID", "0") if state == "active" else "—"}
    return info


def service_states():
    return {unit: details["state"] for unit, details in service_info().items()}


def run_action(action, unit):
    return subprocess.run(service_command(action, unit), check=False).returncode


def read_tail(path, limit=65536, lines=120):
    with path.open("rb") as stream:
        stream.seek(0, 2)
        stream.seek(max(0, stream.tell() - limit))
        data = stream.read(limit)
    return "\n".join(data.decode("utf-8", errors="replace").splitlines()[-lines:])


def configuration(unit):
    if unit not in CONFIGS:
        raise ValueError("Unsupported service")
    return "\n\n".join("# " + str(path) + "\n" + path.read_text() for path in CONFIGS[unit])


def listening_ports():
    result = subprocess.run(
        ["/usr/bin/ss", "--listening", "--tcp", "--numeric",
         "( sport = :80 or sport = :8080 or sport = :3306 )"],
        capture_output=True, text=True, timeout=5, check=True)
    return result.stdout
