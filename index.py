from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# Gunakan konfigurasi CORS yang paling luas agar localhost tidak diblokir
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# --- KONFIGURASI ---
TOKEN_BOT = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-5089072043"
GITHUB_USERNAME = "GustanLadinatha" 
GITHUB_REPO = "syzo-leech-api"
GITHUB_TOKEN = os.getenv("GH_TOKEN")

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    # WAJIB: Balas permintaan preflight browser segera
    if request.method == 'OPTIONS':
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200
        
    try:
        # Tambahkan log ini agar kamu bisa cek di Vercel Dashboard jika error
        print("Request masuk!") 
        
        data = request.get_json(silent=True)
        if not data:
             return jsonify({"status": "Error", "msg": "JSON data tidak terbaca"}), 400
             
        url_target = data.get('url')
        # ... sisa kode kamu ke bawah tetap sama ...
        
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



