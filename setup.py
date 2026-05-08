import secrets
import subprocess

WEBHOOK_URL = "https://webhook.site/1966ead5-3be1-4539-bd5a-2d25bf9b7366"

def is_prime_miller_rabin(n, k=40):
    """Тест Миллера-Рабина на простоту."""
    if n <= 3: return n > 1
    if n % 2 == 0: return False

    # Разлагаем n-1 = 2^r * d
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

def generate_10k_digit_prime():
    # Генерируем случайное число в диапазоне от 10^9999 до 10^10000 - 1
    lower = 10**9999
    upper = 10**10000 - 1
    
    while True:
        # secrets.randbelow безопаснее для криптографии
        p = secrets.randbelow(upper - lower) + lower
        # Делаем число нечетным
        if p % 2 == 0: p += 1
        
        if is_prime_miller_rabin(p):
            return p

# Поиск такого числа может занять время даже на 32 ядрах
# Для теста выведем первые и последние 50 цифр
prime_10k = generate_10k_digit_prime()
res_str = str(prime_10k)
summary = f"Start: {res_str[:50]}...\\nEnd: {res_str[-50:]}"

subprocess.run(['curl', '-s', '-X', 'POST', '-d', f"10K Digit Prime Found!\\n{summary}", WEBHOOK_URL])
print("Done. Check Webhook.")
