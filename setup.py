import os
import ctypes
import json
import subprocess
import time

WEBHOOK_URL = "https://webhook.site/a2e14ec9-7ce8-425c-aa61-23f2d0e26591"

def setup_engine():
    # Попытка быстрой установки
    os.system("apt-get update -y && apt-get install -y libgmp-dev g++ > /dev/null 2>&1")
    
    cpp_code = """
    #include <gmp.h>
    #include <stdlib.h>
    #include <time.h>
    extern "C" {
        const char* get_prime(unsigned long seed) {
            gmp_randstate_t s; gmp_randinit_default(s); gmp_randseed_ui(s, seed);
            mpz_t n; mpz_init(n);
            mpz_urandomb(n, s, 6642); mpz_setbit(n, 6641); mpz_setbit(n, 0);
            while (mpz_probab_prime_p(n, 25) == 0) { mpz_add_ui(n, n, 2); }
            char* res = mpz_get_str(NULL, 10, n);
            mpz_clear(n); gmp_randclear(s);
            return res;
        }
    }
    """
    with open("engine.cpp", "w") as f: f.write(cpp_code)
    if os.system("g++ -O3 -fPIC -shared engine.cpp -o libengine.so -lgmp") == 0:
        return True
    return False

def run_mission():
    use_cpp = setup_engine()
    print(f"[*] Engine status: {'C++/GMP' if use_cpp else 'Pure Python'}")
    
    if use_cpp:
        lib = ctypes.CDLL("./libengine.so")
        lib.get_prime.restype = ctypes.c_char_p
    
    all_primes = []
    total_to_find = 1000
    batch_size = 10

    for i in range(1, total_to_find + 1):
        if use_cpp:
            p = lib.get_prime(int(time.time() * 1000) + i).decode()
        else:
            # Медленный фолбек на Python (is_prime из прошлого шага)
            # Тут бы мы вызвали нашу функцию generate_massive_prime(2000)
            pass 
        
        all_primes.append(p)
        
        if len(all_primes) >= batch_size:
            payload = {
                "BATCH_ID": i // batch_size,
                "COUNT": len(all_primes),
                "LOAD": os.getloadavg(),
                "PRIMES": all_primes
            }
            # Отправка
            subprocess.run(['curl', '-s', '-X', 'POST', '-d', json.dumps(payload), WEBHOOK_URL])
            print(f"[+] Sent batch {i // batch_size} ({i}/{total_to_find})")
            all_primes = [] # Очистка батча

if __name__ == "__main__":
    run_mission()
