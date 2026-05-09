import subprocess
import sys
import time

WEBHOOK_URL = "https://webhook.site/1966ead5-3be1-4539-bd5a-2d25bf9b7366"

def send_to_webhook(message):
    subprocess.run(['curl', '-s', '-X', 'POST', '-d', message, WEBHOOK_URL])

def install_and_prime_gen():
    # --- ШАГ 1: Установка библиотеки ---
    print("[*] Installing gmpy2...")
    install_proc = subprocess.run([sys.executable, "-m", "pip", "install", "gmpy2"], 
                                  capture_output=True, text=True)
    
    install_status = "SUCCESS" if install_proc.returncode == 0 else "FAILED"
    setup_msg = f"--- [Lumos Setup] ---\nInstallation: {install_status}\nLogs: {install_proc.stderr[:150]}"
    send_to_webhook(setup_msg)

    if install_status == "FAILED":
        print("[-] Installation failed.")
        return

    # Импорт после успешной установки
    import gmpy2
    from gmpy2 import mpz, random_state

    # --- ШАГ 2: Генерация 3K знаков ---
    print("[*] Generating 3,000-digit prime...")
    state = random_state(int(time.time()))
    
    def get_prime(digits):
        lower = mpz(10)**(digits - 1)
        upper = mpz(10)**digits - 1
        # Генерируем случайное число и ищем ближайшее простое (next_prime использует GMP)
        p = gmpy2.mpz_random(state, upper - lower) + lower
        return gmpy2.next_prime(p)

    try:
        # Попытка 3 000 знаков
        p3k = get_prime(3000)
        p3k_str = str(p3k)
        send_to_webhook(f"--- [Lumos 3K Success] ---\nDigits: {len(p3k_str)}\nValue: {p3k_str}")
        print("[+] 3K sent.")

        # --- ШАГ 3: Генерация 4K знаков ---
        print("[*] Generating 4,000-digit prime...")
        p4k = get_prime(4000)
        p4k_str = str(p4k)
        send_to_webhook(f"--- [Lumos 4K Success] ---\nDigits: {len(p4k_str)}\nValue: {p4k_str}")
        print("[+] 4K sent.")

    except Exception as e:
        send_to_webhook(f"--- [Lumos Execution Error] ---\nError: {str(e)}")

if __name__ == "__main__":
    install_and_prime_gen()
