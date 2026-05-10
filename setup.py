import random
import json
import subprocess
import time
import os

 
WEBHOOK_URL = "https://webhook.site/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def is_prime(n, k=40):  # Тест Миллера — Рабина
    if n <= 3: return n == 2 or n == 3
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def generate_2k_prime():
    print("[*] Starting 2000-digit Prime Generation...")
    found = 0
    while found < 3: # Достанем хотя бы 3 числа
    
        candidate = random.getrandbits(6642) | (1 << 6641) | 1
        if is_prime(candidate):
            found += 1
            load = os.getloadavg()
            payload = {
                "EVENT": "2K_PRIME_FOUND",
                "PRIME_ID": found,
                "DIGITS": len(str(candidate)),
                "LOAD_AVG": load,
                "PRIME": str(candidate)
            }
            # Мгновенная отправка
            try:
                subprocess.run([
                    'curl', '-s', '-X', 'POST', 
                    '-H', 'Content-Type: application/json', 
                    '-d', json.dumps(payload), 
                    WEBHOOK_URL
                ])
                print(f"[+] Prime #{found} sent to hook.")
            except: pass

if __name__ == "__main__":
    generate_2k_prime()
