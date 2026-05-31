from flask import Flask, request
import requests
import imaplib
import email
import json
import re
from email.header import decode_header

app = Flask(__name__)

BOT_TOKEN = "8604351766:AAHaVEOUyeKX2IrcvNRlHfj_nt3eNqXo5yY"
CHAT_IDS = ["8585638258", "5992758516"]
GMAIL_USER = "mostapha0818@gmail.com"
GMAIL_PASS = "avlv fiwh hoeg tbki"

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_telegram(chat_id, side, ticker, price, tf):
    icon = "\U0001f7e2" if side == "BUY" else "\U0001f534"
    side_ar = "شراء" if side == "BUY" else "بيع"
    msg = f"""{icon} <b>إشارة ICT SMC</b> {icon}
{'─' * 25}
<b>  نوع الصفقة:</b> {side_ar}
<b>  الزوج:</b> {ticker}
<b>  السعر:</b> ${price}
<b>  الإطار:</b> {tf}
{'─' * 25}
<i>FVG + Order Block + Liq + MSS</i>"""
    requests.post(TELEGRAM_URL, json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"})

def check_email():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN FROM "alert@tradingview.com")')
        if status != "OK":
            mail.logout()
            return 0

        ids = messages[0].split()
        count = 0
        for eid in ids:
            status, data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            raw = data[0][1]
            msg = email.message_from_bytes(raw)
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

            # Extract JSON from email body
            json_match = re.search(r'\{[^}]+\}', body)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    side = data.get("side", "N/A")
                    ticker = data.get("ticker", "N/A")
                    price = data.get("price", "N/A")
                    tf = data.get("timeframe", "N/A")
                    for cid in CHAT_IDS:
                        send_telegram(cid, side, ticker, price, tf)
                    count += 1
                except:
                    pass

            mail.store(eid, "+FLAGS", "\\Seen")

        mail.logout()
        return count
    except:
        return -1

@app.route("/check-email", methods=["GET"])
def check_email_endpoint():
    n = check_email()
    if n >= 0:
        return {"checked": True, "signals_found": n}, 200
    return {"error": "email check failed"}, 500

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
        for cid in CHAT_IDS:
            send_telegram(cid, side, ticker, price, tf)
        return {"ok": True}, 200
    return "ICT SMC Bot is running! ✅", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
