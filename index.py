from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)

# MENGIZINKAN SEMUA AKSES (Menghilangkan Error Merah di Browser)
CORS(app, resources={r"/*": {"origins": "*"}})

# Konfigurasi GitHub
# Kamu bisa ganti Token langsung di sini atau via Environment Variable Vercel
GITHUB_TOKEN = "PASTE_TOKEN_GITHUB_KAMU_DISINI" 
GITHUB_REPO = "GustanLadinatha/syzo-leech-api"

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    # Menangani request pengecekan dari browser
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        target_url = data.get('url')

        if not target_url:
            return jsonify({"status": "error", "message": "URL kosong"}), 400

        # Memicu GitHub Actions Dispatch
        dispatch_url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        payload = {
            "event_type": "start-leech",
            "client_payload": {"url": target_url}
        }

        response = requests.post(dispatch_url, json=payload, headers=headers)

        if response.status_code == 204:
            return jsonify({"status": "success", "message": "Worker started!"}), 200
        else:
            return jsonify({"status": "error", "message": response.text}), response.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Wajib untuk Vercel
def handler(event, context):
    return app(event, context)
