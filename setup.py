import http.client
import json
import multiprocessing
import os

# ТВОЙ ХУК
HOOK_DOMAIN = "webhook.site"
HOOK_PATH = "/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def send_post(event):
    try:
        data = json.dumps({"status": event, "load": os.getloadavg()})
        conn = http.client.HTTPSConnection(HOOK_DOMAIN, timeout=5)
        conn.request("POST", HOOK_PATH, data, {"Content-Type": "application/json"})
        response = conn.getresponse()
        print(f"[*] Sent: {event}, Status: {response.status}")
        conn.close()
    except Exception as e:
        print(f"[-] Error: {e}")

def work():
    # Нагрузка на ядро
    while True:
        x = 2**1000000

if __name__ == "__main__":
    # 1. Отправляем статус СТАРТ
    send_post("START_48_CORES")

    # 2. Грузим систему
    cores = multiprocessing.cpu_count()
    for i in range(cores):
        multiprocessing.Process(target=work).start()

    # 3. Отправляем статус ХАЙ_ЛОАД
    send_post("MAX_LOAD_INITIATED")
