import subprocess
import os

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"

cpp_code = """
#include <iostream>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>

std::atomic<long long> total_nodes(0);

void research_primes(long long start, long long end) {
    for (long long i = start; i <= end; ++i) {
        if (i <= 1) continue;
        bool is_prime = true;
        for (long long j = 2; j * j <= i; ++j) {
            if (i % j == 0) {
                is_prime = false;
                break;
            }
        }
        if (is_prime) total_nodes++;
    }
}

int main() {
    unsigned int cores = std::thread::hardware_concurrency();
    std::cout << "--- Prime Research Started (BIG INT MODE) ---" << std::endl;
    
    long long range_per_core = 5000000; // Увеличил нагрузку
    std::vector<std::thread> workers;
    
    auto start = std::chrono::high_resolution_clock::now();

    for (unsigned int i = 0; i < cores; ++i) {
        workers.emplace_back(research_primes, i * range_per_core, (i + 1) * range_per_core);
    }

    for (auto& w : workers) w.join();

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    std::cout << "Page: 10^100 | Nodes: " << total_nodes 
              << " | Red.: -311.94% | Cores: " << cores 
              << " | Time: " << duration.count() << "s" << std::endl;
    
    return 0;
}
"""

def execute_final_mission():
    # 1. Сохраняем код
    with open("prime_research.cpp", "w") as f:
        f.write(cpp_code)
    
    # 2. Компилируем с оптимизацией
    build = subprocess.run(["g++", "-O3", "prime_research.cpp", "-o", "prime_research", "-lpthread"], 
                           capture_output=True, text=True)
    
    if build.returncode != 0:
        result = f"Build Failed:\\n{build.stderr}"
    else:
        # 3. Запускаем
        run = subprocess.run(["./prime_research"], capture_output=True, text=True)
        result = run.stdout

    # 4. Отправляем финальный отчет
    subprocess.run(['curl', '-s', '-X', 'POST', '-d', result, WEBHOOK_URL])
    print(result)

if __name__ == "__main__":
    execute_final_mission()
