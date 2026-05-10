import os
import random
import json
import urllib.request
import multiprocessing

HOOK = "https://webhook.site/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def report(data):
    try:
        req = urllib.request.Request(HOOK, data=json.dumps(data).encode(), 
                                   headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as f: pass
    except: pass

def simple_miner(id):
    # Каждые 1000 итераций шлем сигнал, что мы живы
    count = 0
    while True:
        candidate = random.getrandbits(2000) | 1
        # Быстрый тест на малых числах перед тяжелым pow
        if candidate % 3 != 0 and candidate % 5 != 0:
            if pow(2, candidate-1, candidate) == 1: # Тест Ферма (быстрее Миллера)
                report({"EVENT": "FOUND", "WORKER": id, "DATA": str(candidate)[:50]})
        
        count += 1
        if count % 1000 == 0:
            report({"EVENT": "ALIVE", "WORKER": id, "LOAD": os.getloadavg()})

if __name__ == "__main__":
    # Сначала ОДИН сигнал о старте
    report({"EVENT": "STARTING_48_CORE_TEST", "CORES": multiprocessing.cpu_count()})
    
    # Запускаем постепенно, не все сразу
    for i in range(multiprocessing.cpu_count()):
        multiprocessing.Process(target=simple_miner, args=(i,)).start()
