from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)

# --- KONFIGURASI ---
TOKEN_BOT = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-5089072043"
GITHUB_USERNAME = "Gustan Ladinatha" # <-- Ganti dengan username GitHub kamu
GITHUB_REPO = "syzo-leech-api"         # <-- Ganti dengan nama repository kamu
GITHUB_TOKEN = os.getenv("GH_TOKEN")   # <-- Ganti dengan Token PAT ghp_ kamu

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    if request.method == 'OPTIONS':
        return jsonify({"status": "OK"}), 200
        
    try:
        data = request.get_json(silent=True)
        url_target = data.get('url')
        
        if not url_target:
            return jsonify({"status": "Error", "msg": "URL tidak ditemukan"}), 400

        # 1. Kirim Notifikasi Awal ke Telegram
        tz_jkt = pytz.timezone('Asia/Jakarta')
        waktu_sekarang = datetime.now(tz_jkt).strftime('%H:%M:%S')
        
        pesan_awal = (
            "🚀 *New Request Received*\n\n"
            f"🔗 Target: `{url_target}`\n"
            f"⏰ Time: {waktu_sekarang} WIB\n\n"
            "⏳ _Menghubungi GitHub Worker..._"
        )
        
        requests.post(f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage", json={
            "chat_id": CHAT_ID, 
            "text": pesan_awal,
            "parse_mode": "Markdown"
        })

        # 2. Trigger GitHub Actions (The Worker)
        dispatch_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/dispatches"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "event_type": "start-leech", # Harus sama dengan 'types' di leech.yml
            "client_payload": {"url": url_target}
        }
        
        response_gh = requests.post(dispatch_url, json=payload, headers=headers)

        if response_gh.status_code == 204:
            return jsonify({"status": "Success", "msg": "Worker berhasil dijalankan!"}), 200
        else:
            return jsonify({"status": "Error", "msg": f"Gagal kontak GitHub: {response_gh.text}"}), 500
            
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

