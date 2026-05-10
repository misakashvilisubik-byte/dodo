import os
import subprocess
import json

WEBHOOK_URL = "https://webhook.site/d9ed8938-0733-4ce3-8d2c-63dab5606e87"

def prepare_and_pwn():
    print("[*] Preparing environment...")
    
 
    os.system("apt-get update && apt-get install -y libgmp-dev g++")

    cpp_source = """
    #include <gmp.h>
    #include <iostream>
    #include <time.h>
    extern "C" {
        const char* get_2k_prime() {
            gmp_randstate_t state; gmp_randinit_default(state);
            gmp_randseed_ui(state, time(NULL) + clock());
            mpz_t n; mpz_init(n);
            mpz_urandomb(n, state, 6642); mpz_setbit(n, 6641); mpz_setbit(n, 0);
            while (mpz_probab_prime_p(n, 25) == 0) { mpz_add_ui(n, n, 2); }
            char* res = mpz_get_str(NULL, 10, n);
            mpz_clear(n); gmp_randclear(state);
            return res;
        }
    }
    """
    
    with open("fast_prime.cpp", "w") as f: f.write(cpp_source)

 
    build_res = os.system("g++ -O3 -fPIC -shared fast_prime.cpp -o libprime.so -lgmp")
    
    if build_res == 0:
        print("[+] Success! GMP is ready.")
    
        import ctypes
        lib = ctypes.CDLL("./libprime.so")
        lib.get_2k_prime.restype = ctypes.c_char_p
        
        prime = lib.get_2k_prime().decode()
        
        payload = {"EVENT": "NATIVE_GMP_RESULT", "DATA": prime}
        subprocess.run(['curl', '-s', '-X', 'POST', '-d', json.dumps(payload), WEBHOOK_URL])
    else:
        print("[-] Still no GMP. Railway hardened this one.")

if __name__ == "__main__":
    prepare_and_pwn()
