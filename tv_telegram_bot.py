from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "8604351766:AAHaVEOUyeKX2IrcvNRlHfj_nt3eNqXo5yY"
CHAT_IDS = ["8585638258", "5992758516"]
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
PHOTO_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

def send_signal(chat_id, side, ticker, price, tf, chart_img=None):
    icon = "\U0001f7e2" if side == "BUY" else "\U0001f534"
    side_ar = "شراء" if side == "BUY" else "بيع"

    msg = f"""
{icon} <b>إشارة ICT SMC</b> {icon}
{'─' * 25}
<b>  نوع الصفقة:</b> {side_ar}
<b>  الزوج:</b> {ticker}
<b>  السعر:</b> ${price}
<b>  الإطار:</b> {tf}
{'─' * 25}
<i>FVG + Order Block + سيولة</i>
"""

    if chart_img:
        try:
            img_data = requests.get(chart_img, timeout=10).content
            requests.post(PHOTO_URL, data={
                "chat_id": chat_id,
                "caption": msg,
                "parse_mode": "HTML"
            }, files={"photo": ("chart.jpg", img_data, "image/jpeg")})
            return
        except:
            pass

    requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML"
    })

@app.route("/webhook", methods=["GET", "POST"])
@app.route("/", methods=["GET"])
def home():
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return {"error": "no data"}, 400

        side = data.get("side", "N/A")
        ticker = data.get("ticker", "N/A")
        price = data.get("price", "N/A")
        tf = data.get("timeframe", "N/A")
        chart_img = data.get("chartImg")

        for chat_id in CHAT_IDS:
            send_signal(chat_id, side, ticker, price, tf, chart_img)

        return {"ok": True}, 200
    return "ICT SMC Bot is running! ✅", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
