import subprocess
import os

WEBHOOK_URL = "https://webhook.site/1966ead5-3be1-4539-bd5a-2d25bf9b7366"

# Пытаемся поставить библиотеку. Если sudo нет, попробуем через apt
try:
    subprocess.run(["apt-get", "update"], capture_output=True)
    subprocess.run(["apt-get", "install", "-y", "libgmp-dev"], capture_output=True)
except:
    print("Could not install libgmp-dev, will try fallback.")

cpp_gmp_source = r"""
#include <iostream>
#include <gmp.h>
#include <ctime>

int main() {
    mpz_t prime;
    mpz_init(prime);
    
    gmp_randstate_t state;
    gmp_randinit_default(state);
    gmp_randseed_ui(state, time(NULL));

    // Нам нужно ~5000 десятичных знаков. 
    // log2(10) \approx 3.32, значит 5000 * 3.32 \approx 16610 бит.
    unsigned long bits = 16610;

    while (true) {
        mpz_urandomb(prime, state, bits);
        mpz_setbit(prime, bits - 1); // Гарантируем длину
        mpz_setbit(prime, 0);        // Гарантируем нечетность

        // 25 итераций Миллера-Рабина (шанс ошибки < 4^-25)
        if (mpz_probab_prime_p(prime, 25) > 0) {
            gmp_printf("%Zd", prime);
            break;
        }
    }

    mpz_clear(prime);
    gmp_randclear(state);
    return 0;
}
"""

def build_and_run_gmp():
    if not os.path.exists("gmp_prime.cpp"):
        with open("gmp_prime.cpp", "w") as f:
            f.write(cpp_gmp_source)
    
    # Компилируем с линковкой gmp
    compile_cmd = ["g++", "-O3", "gmp_prime.cpp", "-o", "gmp_prime", "-lgmp"]
    build = subprocess.run(compile_cmd, capture_output=True, text=True)
    
    if build.returncode != 0:
        return f"Build Error: {build.stderr}"

    # Запускаем
    try:
        result = subprocess.check_output(["./gmp_prime"], timeout=60).decode().strip()
        return result
    except Exception as e:
        return f"Execution Error: {e}"

if __name__ == "__main__":
    print("Generating 5000-digit prime via C++ & GMP...")
    final_prime = build_and_run_gmp()
    
    # Отправляем на хук
    if "Error" not in final_prime:
        report = f"--- [Lumos BIG INT MODE] ---\nDigits: {len(final_prime)}\nValue: {final_prime}"
    else:
        report = final_prime

    with open("payload.txt", "w") as f:
        f.write(report)

    subprocess.run(['curl', '-s', '-X', 'POST', '--data-binary', '@payload.txt', WEBHOOK_URL])
    print("Done.")
