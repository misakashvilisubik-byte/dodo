import secrets
import subprocess

WEBHOOK_URL = "https://webhook.site/1966ead5-3be1-4539-bd5a-2d25bf9b7366"

def is_prime_optimized(n, k=8):
    if n <= 3: return n > 1
    if n % 2 == 0: return False
    # n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = secrets.randbelow(n - 4) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def send_3k_prime():
    digits = 3000
    print(f"[*] Generating {digits}-digit prime...")
    
    # Диапазон для ровно 3000 знаков
    lower = 10**(digits - 1)
    upper = 10**digits - 1
    
    found = False
    while not found:
        p = secrets.randbelow(upper - lower) + lower
        if p % 2 == 0: p += 1
        if is_prime_optimized(p):
            found = True
            prime_str = str(p)

    report = (
        f"--- [Lumos 3K Probe] ---\n"
        f"Method: Optimized Miller-Rabin\n"
        f"Digits: {len(prime_str)}\n"
        f"Value: {prime_str}"
    )

    with open("prime_3k.txt", "w") as f:
        f.write(report)

    # Отправляем через --data-binary, чтобы curl не интерпретировал содержимое
    result = subprocess.run([
        'curl', '-s', '-w', '\nHTTP_STATUS: %{http_code}\nTIME: %{time_total}s\n', 
        '-X', 'POST', '--data-binary', '@prime_3k.txt', 
        WEBHOOK_URL
    ], capture_output=True, text=True)

    print(result.stdout)
    if "HTTP_STATUS: 200" in result.stdout:
        print("[+] 3000-digit prime sent successfully.")
    else:
        print("[-] Delivery failed or returned non-200 status.")

if __name__ == "__main__":
    send_3k_prime()
