from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time
from datetime import datetime
import pytz

app = Flask(__name__)

# FIX CORS: Memberikan izin penuh agar tidak diblokir browser saat testing lokal
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

# Database sementara di memori server
db_links = {}

@app.route('/')
def home():
    return "Syzo API is Online!", 200

# ROUTE UNTUK MENERIMA LINK DARI GITHUB
@app.route('/update_link', methods=['POST'])
def update_link():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "Error", "msg": "No data received"}), 400
            
        run_id = str(data.get('run_id'))
        if run_id:
            # Simpan data lengkap dari GitHub Worker
            db_links[run_id] = {
                "url": data.get('download_url'),
                "filename": data.get('filename', 'File Ready'),
                "md5": data.get('md5', '-'),
                "status": "Completed" # Tandai sebagai Completed untuk Frontend
            }
            return jsonify({"status": "Success"}), 200
        return jsonify({"status": "Error", "msg": "Missing run_id"}), 400
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

@app.route('/get_link/<run_id>', methods=['GET', 'OPTIONS'])
def get_link(run_id):
    if request.method == 'OPTIONS':
        return '', 200
        
    data = db_links.get(str(run_id))
    if data:
        # Jika data ditemukan, kirim ke frontend
        return jsonify({"status": "Completed", "data": data}), 200
    
    # Jika data belum masuk dari GitHub, kirim status Processing
    # HTTP 200 tetap digunakan agar browser tidak menampilkan error merah
    return jsonify({"status": "Processing"}), 200

@app.route('/leech', methods=['POST'])
def leech():
    try:
        data = request.get_json(silent=True)
        url_target = data.get('url')
        if not url_target: return jsonify({"status": "Error"}), 400

        # Notif Telegram
        tz_jkt = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz_jkt).strftime('%H:%M:%S')
        requests.post(f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage", json={
            "chat_id": CHAT_ID, 
            "text": f"🚀 *New Request*\n🔗 `{url_target}`\n⏰ {waktu}", 
            "parse_mode": "Markdown"
        })

        # Trigger GitHub
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        res_gh = requests.post(
            f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/dispatches", 
            json={"event_type": "start-leech", "client_payload": {"url": url_target}}, 
            headers=headers
        )

        if res_gh.status_code == 204:
            # Tunggu sebentar agar GitHub sempat membuat Run ID
            time.sleep(5) 
            run_data = requests.get(
                f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/actions/runs?per_page=1", 
                headers=headers
            ).json()
            
            rid = run_data['workflow_runs'][0]['id'] if run_data.get('workflow_runs') else None
            return jsonify({"status": "Success", "run_id": rid}), 200
            
        return jsonify({"status": "Error", "gh_status": res_gh.status_code}), 500
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

@app.route('/cancel', methods=['POST'])
def cancel():
    try:
        data = request.get_json(silent=True)
        rid = data.get('run_id')
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        requests.post(f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/actions/runs/{rid}/cancel", headers=headers)
        return jsonify({"status": "Success"}), 200
    except:
        return jsonify({"status": "Error"}), 500
