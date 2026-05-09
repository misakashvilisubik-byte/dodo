import subprocess
import os
import time

WEBHOOK_URL = "https://webhook.site/1966ead5-3be1-4539-bd5a-2d25bf9b7366"

# C++ код для генерации кандидата и базовой проверки
cpp_code = r"""
#include <iostream>
#include <vector>
#include <string>
#include <random>

// Простая функция для генерации случайных цифр
int main() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> first_digit(1, 9);
    std::uniform_int_distribution<> other_digits(0, 9);

    std::string prime_candidate = "";
    prime_candidate += std::to_string(first_digit(gen));
    
    for(int i = 0; i < 2998; ++i) {
        prime_candidate += std::to_string(other_digits(gen));
    }
    
    // Гарантируем нечетность
    int last = other_digits(gen);
    if (last % 2 == 0) last++;
    prime_candidate += std::to_string(last);

    std::cout << prime_candidate;
    return 0;
}
"""

def send(msg):
    subprocess.run(['curl', '-s', '-X', 'POST', '--data-urlencode', f"payload={msg}", WEBHOOK_URL])

def run_cpp_task():
    send("[*] Stage: Compiling C++ Engine...")
    
    with open("engine.cpp", "w") as f:
        f.write(cpp_code)
    
    # Компиляция
    compile_proc = subprocess.run(["g++", "-O3", "engine.cpp", "-o", "engine"], capture_output=True, text=True)
    
    if compile_proc.returncode != 0:
        send(f"[-] C++ Compilation Failed: {compile_proc.stderr}")
        return

    send("[*] Stage: C++ Engine Compiled. Searching for 3K prime...")
    
    # Запускаем C++ для генерации числа
    # Python берет на себя тяжелую математику проверки (is_prime)
    raw_candidate = subprocess.check_output(["./engine"]).decode().strip()
    
    # Используем встроенный pow() Python для проверки (он на C, это быстро)
    candidate_int = int(raw_candidate)
    
    start_time = time.time()
    # Быстрая проверка Ферма перед отправкой
    if pow(2, candidate_int - 1, candidate_int) == 1:
        duration = time.time() - start_time
        report = (
            f"--- [Lumos C++ x Python Success] ---\n"
            f"Digits: {len(raw_candidate)}\n"
            f"Generation: C++ (O3)\n"
            f"Verification: Native C-API\n"
            f"Time: {duration:.4f}s\n"
            f"Value: {raw_candidate}"
        )
        send(report)
        print("[+] 3K Prime sent successfully.")
    else:
        # Если не прошло, пробуем еще раз (рекурсивно или в цикле)
        print("[-] Candidate failed Fermat test, retrying...")
        run_cpp_task()

if __name__ == "__main__":
    run_cpp_task()
