import os
import requests
import time

TELEGRAM_TOKEN = os.getenv("8655168763:AAETY-r50KpEc6C8ouPHzuJFWh3q5rXMtAw")
CHAT_ID = os.getenv("2072644841")

rodando = True
ultimo_update_id = None

def enviar(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Erro Telegram:", e)

def comandos():
    global rodando, ultimo_update_id

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        data = requests.get(url, timeout=10).json()

        for update in data.get("result", []):
            uid = update["update_id"]

            if ultimo_update_id and uid <= ultimo_update_id:
                continue

            ultimo_update_id = uid

            if "message" in update:
                texto = update["message"].get("text", "")

                if texto == "/ligar":
                    rodando = True
                    enviar("✅ BOT LIGADO")

                elif texto == "/desligar":
                    rodando = False
                    enviar("❌ BOT DESLIGADO")

    except Exception as e:
        print("Erro comandos:", e)

def preco_btc():
    try:
        url = "https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT"
        data = requests.get(url, timeout=10).json()
        return float(data["result"]["list"][0]["lastPrice"])
    except:
        return None

def rodar():
    while True:
        try:
            comandos()

            if rodando:
                preco = preco_btc()

                if preco:
                    enviar(f"💰 BTC/USDT: {preco}")
                    print("Enviado preço")

                time.sleep(60)
            else:
                print("Pausado")
                time.sleep(10)

        except Exception as e:
            print("Erro geral:", e)
            time.sleep(30)

rodar()
