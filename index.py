from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime # Import datetime
import pytz # Import pytz untuk timezone

app = Flask(__name__)
CORS(app)

TOKEN = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-5089072043"

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    if request.method == 'OPTIONS':
        return jsonify({"status": "OK"}), 200
    try:
        data = request.get_json(silent=True)
        url_target = data.get('url')
        
        # --- SET TIMEZONE KE WIB ---
        tz_jkt = pytz.timezone('Asia/Jakarta')
        waktu_sekarang = datetime.now(tz_jkt).strftime('%H:%M:%S')
        # ---------------------------

        pesan = (
            "🚀 *New Leech Request*\n\n"
            f"Target: {url_target}\n"
            f"Clock: {waktu_sekarang} WIB"
        )
        
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(api_url, json={
            "chat_id": CHAT_ID, 
            "text": pesan,
            "parse_mode": "Markdown"
        }, timeout=15)
        
        return jsonify({"status": "Success", "msg": "Terkirim!"}), 200
            
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500
