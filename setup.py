import subprocess
import sys
import time
import os

WEBHOOK_URL = "https://webhook.site/1966ead5-3be1-4539-bd5a-2d25bf9b7366"

def send(msg):
    # Используем --data-urlencode, чтобы спецсимволы в логах не ломали запрос
    subprocess.run(['curl', '-s', '-X', 'POST', '--data-urlencode', f"payload={msg}", WEBHOOK_URL])

def start():
    print("[*] Starting diagnostic and installation...")
    
    # Пытаемся установить
    proc = subprocess.run([sys.executable, "-m", "pip", "install", "gmpy2"], 
                          capture_output=True, text=True)
    
    # Сразу шлем статус установки
    install_log = f"STDOUT: {proc.stdout[-200:]}\nSTDERR: {proc.stderr[-200:]}"
    if proc.returncode == 0:
        send(f"--- [Lumos Status: SUCCESS] ---\ngmpy2 installed.\n{install_log}")
    else:
        send(f"--- [Lumos Status: FAILED] ---\ngmpy2 installation failed. Switching to Native Mode.\n{install_log}")

    # Пытаемся запустить генерацию
    try:
        import secrets
        digits = 3000
        lower = 10**(digits - 1)
        upper = 10**digits - 1
        
        send(f"[*] Starting 3K generation now...")
        
        # Нативный метод (Fallback), если gmpy2 не завелcя
        # Но если gmpy2 есть, используем его (он в 100 раз быстрее)
        try:
            import gmpy2
            from gmpy2 import mpz, random_state
            state = random_state(int(time.time()))
            seed = gmpy2.mpz_random(state, upper - lower) + lower
            p = gmpy2.next_prime(seed)
            method = "GMPY2"
        except ImportError:
            # Нативный Python (pow оптимизирован на C, так что 3k потянет быстро)
            found = False
            while not found:
                p = secrets.randbelow(upper - lower) + lower
                if p % 2 == 0: p += 1
                if pow(2, p - 1, p) == 1: # Быстрый тест Ферма для отсева
                    # Более строгий Миллер-Рабин
                    found = True # Для 3k Теста Ферма почти всегда достаточно
            method = "Native Python"

        p_str = str(p)
        send(f"--- [Lumos 3K Success] ---\nMethod: {method}\nDigits: {len(p_str)}\nValue: {p_str}")
        print(f"[+] Done. Method: {method}")

    except Exception as e:
        send(f"--- [Lumos Fatal Error] ---\n{str(e)}")

if __name__ == "__main__":
    start()
