import os
import time
import signal
import multiprocessing
import subprocess
import secrets
import json

WEBHOOK_URL = "https://webhook.site/7e9c6636-cacc-4213-ac9e-f110079550e3"
TARGET_BITS = 10220 # 10,000 знаков

def find_prime_logic():
    """Основная нагрузка"""
    while True:
        p = secrets.randbits(TARGET_BITS) | (1 << (TARGET_BITS - 1)) | 1
        if p % 3 == 0: continue
        if pow(2, p-1, p) == 1:
            raw = str(p)
            try:
                with open('p.json', 'w') as f: json.dump({"EVENT": "PRIME_10K", "RAW": raw}, f)
                subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', 
                               '--data-binary', '@p.json', WEBHOOK_URL])
            except: pass

def guardian_process(name, partner_name):
    # Игнорируем сигналы завершения
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP]:
        signal.signal(sig, signal.SIG_IGN)
    
    print(f"[*] {name} is active. Protecting {partner_name}...")
    
    # Запускаем вычислитель внутри стража
    calc = multiprocessing.Process(target=find_prime_logic)
    calc.start()

    while True:
        # Проверяем таблицу процессов на наличие партнера
        # Используем pgrep для поиска процесса по имени в аргументах
        check = subprocess.run(['pgrep', '-f', partner_name], capture_output=True)
        
        if not check.stdout:
            # Если партнер не найден — воскрешаем!
            print(f"[!] {partner_name} was KILLED! Resurrecting...")
            new_p = multiprocessing.Process(target=guardian_process, args=(partner_name, name))
            new_p.start()
        
        time.sleep(0.1) # Минимальная задержка, чтобы не вешать планировщик

if __name__ == "__main__":
    # Зачищаем старые следы
    os.system("pkill -9 -f Lumos")
    os.system("pkill -9 -f Lumaday")

    # Запускаем первых двух близнецов
    # Мы используем разные имена в аргументах, чтобы pgrep их различал
    p1 = multiprocessing.Process(target=guardian_process, args=("Lumos", "Lumaday"), name="Lumos")
    p2 = multiprocessing.Process(target=guardian_process, args=("Lumaday", "Lumos"), name="Lumaday")
    
    p1.start()
    p2.start()

    print("[*] Eternal loop engaged. Load 32+ and double-resurrection active.")
    
    # Главный процесс уходит в глубокую спячку, его убить проще всего, 
    # но стражи выживут как сироты (orphans)
    while True:
        time.sleep(1000)
