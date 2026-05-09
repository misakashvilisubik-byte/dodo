import subprocess
import sys
import time

WEBHOOK_URL = "https://webhook.site/1966ead5-3be1-4539-bd5a-2d25bf9b7366"

def send_status(msg):
    subprocess.run(['curl', '-s', '-X', 'POST', '-d', msg, WEBHOOK_URL])

def run_prime_step():
    # Сообщение о начале
    send_status("--- [Lumos Status] ---\ngmpy2 is active. Starting 3,000-digit calculation...")

    try:
        import gmpy2
        from gmpy2 import mpz, random_state

        # Инициализация
        state = random_state(int(time.time()))
        start = time.time()

        # Генерация 3000 знаков
        lower = mpz(10)**2999
        upper = mpz(10)**3000 - 1
        seed = gmpy2.mpz_random(state, upper - lower) + lower
        
        # Поиск ближайшего простого (GMP-оптимизация)
        prime_3k = gmpy2.next_prime(seed)
        
        end = time.time()
        prime_str = str(prime_3k)

        # Формируем финальный отчет
        report = (
            f"--- [Lumos 3K Success] ---\n"
            f"Execution Time: {end - start:.2f}s\n"
            f"Digits: {len(prime_str)}\n"
            f"Prime: {prime_str}"
        )
        
        send_status(report)
        print(f"[+] 3K generated in {end - start:.2f}s. Check webhook.")

    except Exception as e:
        send_status(f"--- [Lumos Error] ---\n{str(e)}")

if __name__ == "__main__":
    run_prime_step()
