import secrets
import json
import subprocess
import multiprocessing as mp

WEBHOOK_URL = "https://webhook.site/1966ead5-3be1-4539-bd5a-2d25bf9b7366"

def is_prime_miller_rabin(n, k=40):
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

def search_worker(found_event, result_queue):
    lower = 10**4999
    upper = 10**5000 - 1
    while not found_event.is_set():
        p = secrets.randbelow(upper - lower) + lower
        if p % 2 == 0: p += 1
        if is_prime_miller_rabin(p, k=10): # Уменьшил k для скорости первого нахождения
            result_queue.put(p)
            found_event.set()
            break

if __name__ == "__main__":
    print(f"--- Launching Prime Search on 32 Cores ---")
    found_event = mp.Event()
    result_queue = mp.Queue()
    
    # Запускаем процессы на все ядра
    processes = [mp.Process(target=search_worker, args=(found_event, result_queue)) for _ in range(32)]
    
    for p in processes:
        p.start()
    
    # Ждем результата
    prime_10k = result_queue.get()
    
    for p in processes:
        p.terminate()

    prime_str = str(prime_10k)
    
    # Формируем отчет
    payload = {
        "status": "Lumos Lumaday Success",
        "digits": len(prime_str),
        "first_50": prime_str[:50],
        "last_50": prime_str[-50:],
        "full_prime": prime_str # Весь гигант уйдет в JSON теле
    }

    # Отправляем через временный файл, чтобы не перегружать bash
    with open("result.json", "w") as f:
        json.dump(payload, f)

    subprocess.run([
        'curl', '-s', '-H', 'Content-Type: application/json', 
        '-X', 'POST', '-d', '@result.json', WEBHOOK_URL
    ])
    
    print(f"Sent! Check your webhook. Prime starts with: {prime_str[:10]}")
