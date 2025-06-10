import requests
import time
from datetime import datetime, timedelta

TELEGRAM_TOKEN = '7672788217:AAHZH60weMIa-ofK9DW6gCRmLQb4PUG0eRU'
CHAT_ID = '684170730'

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=payload)

def get_prices():
    url = 'https://api.binance.com/api/v3/ticker/price'
    return {item['symbol']: float(item['price']) for item in requests.get(url).json()}

price_history = {}

send_telegram_message("🚀 Bot başlatıldı. Binance verileri takip ediliyor...")

while True:
    try:
        now = datetime.utcnow()
        print(f"{now.strftime('%H:%M:%S')} - Fiyatlar kontrol ediliyor...")

        prices = get_prices()

        for symbol, price in prices.items():
            if not symbol.endswith('USDT'):
                continue

            if symbol not in price_history:
                price_history[symbol] = []

            price_history[symbol].append((now, price))

            # Sadece son 1 dakikalık verileri tut
            price_history[symbol] = [(t, p) for t, p in price_history[symbol] if now - t <= timedelta(minutes=1)]

            # Eski fiyata göre yüzde değişimi kontrol et
            if len(price_history[symbol]) >= 2:
                old_price = price_history[symbol][0][1]
                if old_price == 0:
                    continue
                change_percent = ((price - old_price) / old_price) * 100
                if change_percent >= 2:
                    send_telegram_message(f"📈 {symbol} son 1 dakikada %{change_percent:.2f} yükseldi!\nŞu anki fiyat: {price}")
                    price_history[symbol] = []  # Aynı coin için tekrar uyarı vermemesi için sıfırla

        time.sleep(20)

    except Exception as e:
        send_telegram_message(f"⚠️ Hata oluştu: {e}")
        time.sleep(60)
