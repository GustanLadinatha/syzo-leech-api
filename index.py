from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time # Tambahan untuk jeda ambil ID
from datetime import datetime
import pytz

app = Flask(__name__)

# Konfigurasi CORS
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

@app.route('/')
def home():
    return "Syzo API is Running! Route /leech is active.", 200

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200
        
    try:
        print("Request masuk!") 
        data = request.get_json(silent=True)
        if not data:
             return jsonify({"status": "Error", "msg": "JSON data tidak terbaca"}), 400
             
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

        # 2. Trigger GitHub Actions
        dispatch_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/dispatches"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "event_type": "start-leech",
            "client_payload": {"url": url_target}
        }
        
        response_gh = requests.post(dispatch_url, json=payload, headers=headers)

        if response_gh.status_code == 204:
            # --- TAMBAHAN: AMBIL RUN ID AGAR BISA DI-CANCEL ---
            time.sleep(1.5) # Tunggu GitHub bikin record
            runs_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/actions/runs?per_page=1"
            run_data = requests.get(runs_url, headers=headers).json()
            run_id = run_data['workflow_runs'][0]['id'] if run_data.get('workflow_runs') else None
            
            return jsonify({
                "status": "Success", 
                "msg": "Worker berhasil dijalankan!",
                "run_id": run_id # Kirim ID ke frontend
            }), 200
        else:
            return jsonify({"status": "Error", "msg": f"Gagal kontak GitHub: {response_gh.text}"}), 500
            
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

# --- ROUTE TAMBAHAN UNTUK CANCEL (BARU) ---
@app.route('/cancel', methods=['POST'])
def cancel():
    try:
        data = request.get_json()
        run_id = data.get('run_id')
        file_name = data.get('file_name', 'Unknown File')

        if not run_id:
            return jsonify({"status": "Error", "msg": "Run ID tidak ditemukan"}), 400

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        # 1. Matikan proses di GitHub
        cancel_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/actions/runs/{run_id}/cancel"
        requests.post(cancel_url, headers=headers)

        # 2. Kirim notifikasi pembatalan ke Telegram
        pesan_cancel = (
            "❌ *Proses Dibatalkan*\n\n"
            f"📁 File: `{file_name}`\n"
            "⚠️ Status: _Aborted by User via Web_"
        )
        requests.post(f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage", json={
            "chat_id": CHAT_ID, 
            "text": pesan_cancel, 
            "parse_mode": "Markdown"
        })

        return jsonify({"status": "Success", "msg": "Proses berhasil dihentikan"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
