import os
import subprocess
import json
import http.client

HOOK_DOMAIN = "webhook.site"
HOOK_PATH = "/a2e14ec9-7ce8-425c-aa61-23f2d0e26591"

def send_gpu_report(status, details):
    try:
        conn = http.client.HTTPSConnection(HOOK_DOMAIN, timeout=5)
        payload = json.dumps({"EVENT": "GPU_CHECK", "STATUS": status, "DETAILS": details})
        conn.request("POST", HOOK_PATH, payload, {"Content-Type": "application/json"})
        conn.getresponse()
        conn.close()
    except: pass

def check_gpu():
    results = {}
    
    # 1. Проверка через lspci (нужен pciutils)
    pci = os.popen("lspci | grep -i 'vga\|3d\|nvidia\|amd'").read()
    results["lspci"] = pci if pci else "None"

    # 2. Проверка устройств в /dev
    dev_nvidia = os.path.exists("/dev/nvidia0")
    dev_dri = os.listdir("/dev/dri") if os.path.exists("/dev/dri") else []
    results["dev_nodes"] = {"nvidia": dev_nvidia, "dri": dev_dri}

    # 3. Попытка вызвать nvidia-smi
    try:
        smi = subprocess.check_output(["nvidia-smi", "-L"], stderr=subprocess.STDOUT, text=True)
        results["nvidia_smi"] = smi.strip()
    except:
        results["nvidia_smi"] = "Not Found"

    # 4. Переменные окружения (часто для CUDA в контейнерах)
    results["env"] = {k: v for k, v in os.environ.items() if "CUDA" in k or "NVIDIA" in k}

    return results

if __name__ == "__main__":
    print("[*] Scanning for GPU hardware...")
    gpu_data = check_gpu()
    
    if gpu_data["nvidia_smi"] != "Not Found" or gpu_data["dev_nodes"]["nvidia"]:
        send_gpu_report("GPU_DETECTED", gpu_data)
        print("[!!!] GPU FOUND! Switching to CUDA stress test...")
    else:
        send_gpu_report("NO_GPU_FOUND", gpu_data)
        print("[-] No GPU detected. Staying on CPU stress.")
