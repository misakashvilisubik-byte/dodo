import os
import ctypes
import json
import subprocess
import time

WEBHOOK_URL = "https://webhook.site/a2e14ec9-7ce8-425c-aa61-23f2d0e26591"

def setup_engine():
    # Без GMP этот масштаб не взять
    os.system("apt-get update -y && apt-get install -y libgmp-dev g++ > /dev/null 2>&1")
    
    cpp_code = """
    #include <gmp.h>
    #include <stdlib.h>
    #include <time.h>
    #include <iostream>

    extern "C" {
        const char* get_goliath_prime(unsigned long seed) {
            gmp_randstate_t s; gmp_randinit_default(s); gmp_randseed_ui(s, seed);
            mpz_t n; mpz_init(n);
            
            // 33220 бит ≈ 10000 десятичных знаков
            mpz_urandomb(n, s, 33220); 
            mpz_setbit(n, 33219); // Гарантируем длину
            mpz_setbit(n, 0);     // Только нечетные
            
            // Тест Миллера-Рабина
            // Для 10к знаков 20-30 итераций достаточно для практической достоверности
            while (mpz_probab_prime_p(n, 25) == 0) {
                mpz_add_ui(n, n, 2);
            }
            
            char* res = mpz_get_str(NULL, 10, n);
            mpz_clear(n); gmp_randclear(s);
            return res;
        }
    }
    """
    with open("goliath.cpp", "w") as f: f.write(cpp_code)
    # Компиляция с O3 — на таких числах каждый такт важен
    if os.system("g++ -O3 -fPIC -shared goliath.cpp -o libgoliath.so -lgmp") == 0:
        return True
    return False

def run_mission():
    use_cpp = setup_engine()
    if not use_cpp:
        print("[-] GMP setup failed. Goliath requires C++.")
        return

    lib = ctypes.CDLL("./libgoliath.so")
    lib.get_goliath_prime.restype = ctypes.c_char_p
    
    print("[*] Generating 10,000 digit prime... This will spike the CPU.")
    
    start_t = time.time()
    # Берем сид от времени
    p_raw = lib.get_goliath_prime(int(time.time())).decode()
    duration = time.time() - start_t
    
    payload = {
        "EVENT": "GOLIATH_PRIME_FOUND",
        "DIGITS": len(p_raw),
        "SEARCH_TIME_SEC": round(duration, 2),
        "LOAD": os.getloadavg(),
        "DATA": p_raw
    }
    
    # Отправка. ВНИМАНИЕ: Тело запроса будет около 10КБ.
    subprocess.run(['curl', '-s', '-X', 'POST', '-d', json.dumps(payload), WEBHOOK_URL])
    print(f"[+] Goliath found in {duration:.2f}s and sent to hook.")

if __name__ == "__main__":
    run_mission()
