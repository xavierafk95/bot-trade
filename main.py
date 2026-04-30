import requests
import time

TOKEN = "8655168763:AAETY-r50KpEc6C8ouPHzuJFWh3q5rXMtAw"
CHAT_ID = "2072644841"

while True:
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": "🚀 BOT ONLINE"}
        )
        print("Enviou mensagem")
        time.sleep(30)
    except Exception as e:
        print("Erro:", e)
        time.sleep(30)
