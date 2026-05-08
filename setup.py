import os
import multiprocessing
import secrets
import json
import subprocess
import time
import signal

WEBHOOK_URL = "https://webhook.site/7e9c6636-cacc-4213-ac9e-f110079550e3"
TARGET_BITS = 33220  # Ровно 10,000 десятичных знаков

def send_data(payload):
    try:
        # Используем файл для стабильной передачи больших данных
        with open('msg.json', 'w') as f:
            json.dump(payload, f)
        subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', 
                       '--data-binary', '@msg.json', WEBHOOK_URL], timeout=20)
    except:
        pass

def beacon_loop():
    """Маяк: отправляет нагрузку каждые 5 минут"""
    while True:
        time.sleep(300) # 5 минут
        load = os.getloadavg()
        send_data({
            "EVENT": "HEARTBEAT_LOAD",
            "LOAD_1_5_15": load,
            "STATUS": "STILL_MINING_50K",
            "UPTIME_SEC": time.process_time()
        })

def prime_miner():
    # Игнорируем сигналы, чтобы не прерывать вычисления
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    
    while True:
        # Генерация кандидата
        p = secrets.randbits(TARGET_BITS) | (1 << (TARGET_BITS - 1)) | 1
        
        # Быстрое сито
        if p % 3 == 0 or p % 5 == 0 or p % 7 == 0:
            continue
            
        # Тест Ферма (основание 2) - самый быстрый для таких гигантов
        if pow(2, p-1, p) == 1:
            res = str(p)
            send_data({
                "EVENT": "PRIME_50K_FOUND",
                "DIGITS": len(res),
                "LOAD_AT_FIND": os.getloadavg(),
                "RAW": res
            })

if __name__ == "__main__":
    cores = multiprocessing.cpu_count()
    print(f"[*] Starting 50K Blast on {cores} cores.")

    # Запускаем Маяк в отдельном процессе
    multiprocessing.Process(target=beacon_loop, daemon=True).start()

    # Запускаем Армию Майнеров
    for _ in range(cores):
        p = multiprocessing.Process(target=prime_miner)
        p.daemon = True
        p.start()

    # Главный процесс для логов в консоль Railway
    try:
        while True:
            print(f"[!] Current Load: {os.getloadavg()}")
            time.sleep(60)
    except:
        pass
