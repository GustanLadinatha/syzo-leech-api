from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time
from datetime import datetime
import pytz

app = Flask(__name__)

# Mengaktifkan CORS agar bisa diakses dari localhost maupun domain web
CORS(app, resources={r"/*": {"origins": "*"}})

# --- KONFIGURASI ---
TOKEN_BOT = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-5089072043"
GITHUB_USERNAME = "GustanLadinatha" 
GITHUB_REPO = "syzo-leech-api"
GITHUB_TOKEN = os.getenv("GH_TOKEN")

@app.route('/')
def home():
    return "Syzo API is Running! Route /leech and /cancel are active.", 200

# --- ROUTE UNTUK MEMULAI LEECH ---
@app.route('/leech', methods=['POST'])
def leech():
    try:
        print("Request Leech masuk!") 
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

        # 2. Trigger GitHub Actions Dispatch
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
            # --- PERUBAHAN DISINI (SAFE START DELAY) ---
            # Kita beri jeda 4 detik agar GitHub selesai mendaftarkan Run ID.
            # Tanpa jeda ini, tombol cancel di web sering 'gagal' karena ID belum ada.
            time.sleep(4) 
            
            # Ambil Run ID terbaru
            runs_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/actions/runs?per_page=1"
            run_data = requests.get(runs_url, headers=headers).json()
            
            run_id = None
            if run_data.get('workflow_runs'):
                run_id = run_data['workflow_runs'][0]['id']
            
            return jsonify({
                "status": "Success", 
                "msg": "Worker is warming up...",
                "run_id": run_id
            }), 200
        else:
            return jsonify({"status": "Error", "msg": f"Gagal kontak GitHub: {response_gh.text}"}), 500
            
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

# --- ROUTE UNTUK MEMBATALKAN LEECH ---
@app.route('/cancel', methods=['POST'])
def cancel():
    try:
        print("Request Cancel masuk!")
        data = request.get_json(silent=True)
        run_id = data.get('run_id')
        file_name = data.get('file_name', 'User Request')

        if not run_id:
            return jsonify({"status": "Error", "msg": "Run ID tidak ditemukan"}), 400

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        # 1. Kirim perintah Cancel ke API GitHub
        cancel_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/actions/runs/{run_id}/cancel"
        gh_resp = requests.post(cancel_url, headers=headers)

        # 2. Kirim Notifikasi Pembatalan ke Telegram
        pesan_cancel = (
            "❌ *PROSES DIBATALKAN*\n\n"
            f"📁 Target: `{file_name}`\n"
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
