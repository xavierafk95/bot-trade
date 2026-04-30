import requests
import pandas as pd
import time
from datetime import datetime

TOKEN = "S8655168763:AAETY-r50KpEc6C8ouPHzuJFWh3q5rXMtAw"
CHAT_ID = "2072644841"

rodando = True
ultimo_update_id = None
ultimo_sinal = None
ultimo_horario_sinal = 0

# CONFIG
COOLDOWN = 1800  # 30 minutos entre sinais

def enviar(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
    except Exception as e:
        print("Erro Telegram:", e)

def comandos():
    global rodando, ultimo_update_id

    try:
        data = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getUpdates",
            timeout=10
        ).json()

        for u in data.get("result", []):
            uid = u["update_id"]

            if ultimo_update_id and uid <= ultimo_update_id:
                continue

            ultimo_update_id = uid

            if "message" in u:
                txt = u["message"].get("text", "")

                if txt == "/ligar":
                    rodando = True
                    enviar("✅ BOT LIGADO")

                elif txt == "/desligar":
                    rodando = False
                    enviar("❌ BOT DESLIGADO")

    except Exception as e:
        print("Erro comandos:", e)

def pegar_dados(interval):
    try:
        url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval={interval}&limit=200"
        data = requests.get(url, timeout=10).json()

        if "result" not in data or not data["result"]["list"]:
            return None

        df = pd.DataFrame(data['result']['list'])
        df = df.iloc[:, :6]
        df.columns = ['time','open','high','low','close','volume']
        df = df[::-1]
        df['close'] = df['close'].astype(float)

        return df

    except:
        return None

def indicadores(df):
    df['ema50'] = df['close'].ewm(span=50).mean()
    df['ema200'] = df['close'].ewm(span=200).mean()

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    exp1 = df['close'].ewm(span=12).mean()
    exp2 = df['close'].ewm(span=26).mean()
    df['macd'] = exp1 - exp2
    df['signal'] = df['macd'].ewm(span=9).mean()

    return df

def mercado_lateral(df, preco):
    return abs(df.iloc[-1]['ema50'] - df.iloc[-1]['ema200']) < preco * 0.002

def analisar():
    global ultimo_sinal, ultimo_horario_sinal

    agora = time.time()

    if agora - ultimo_horario_sinal < COOLDOWN:
        return

    df_15 = pegar_dados("15")
    df_1h = pegar_dados("60")

    if df_15 is None or df_1h is None:
        return

    df_15 = indicadores(df_15)
    df_1h = indicadores(df_1h)

    if len(df_15) < 2:
        return

    u = df_15.iloc[-1]
    a = df_15.iloc[-2]
    u1h = df_1h.iloc[-1]

    preco = u['close']
    hora = datetime.utcnow().strftime('%H:%M')

    if mercado_lateral(df_15, preco):
        return

    tendencia_alta = u['ema50'] > u['ema200'] and u1h['ema50'] > u1h['ema200']
    tendencia_baixa = u['ema50'] < u['ema200'] and u1h['ema50'] < u1h['ema200']

    sinal = None

    if (
        tendencia_alta and
        a['macd'] < a['signal'] and
        u['macd'] > u['signal'] and
        50 < u['rsi'] < 70
    ):
        sinal = "COMPRA"
        sl = preco * 0.985
        tp = preco * 1.03

    elif (
        tendencia_baixa and
        a['macd'] > a['signal'] and
        u['macd'] < u['signal'] and
        30 < u['rsi'] < 50
    ):
        sinal = "VENDA"
        sl = preco * 1.015
        tp = preco * 0.97

    if sinal and sinal != ultimo_sinal:
        enviar(f"""
🚨 {sinal} BTC/USDT

💰 Preço: {preco:.2f}
📊 RSI: {u['rsi']:.2f}

🛑 SL: {sl:.2f}
🎯 TP: {tp:.2f}

⏰ {hora} UTC
""")

        ultimo_sinal = sinal
        ultimo_horario_sinal = agora

def rodar():
    while True:
        try:
            comandos()

            if rodando:
                analisar()
                print("Rodando PRO...")
                time.sleep(60)
            else:
                time.sleep(10)

        except Exception as e:
            print("Erro geral:", e)
            time.sleep(30)

rodar()
