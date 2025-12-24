from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)

# 1. MENGIZINKAN CORS (Menghilangkan error merah di console browser)
# Ini akan mengizinkan website kamu (127.0.0.1 atau domain lain) untuk memanggil API ini
CORS(app, resources={r"/*": {"origins": "*"}})

# Konfigurasi GitHub (Sesuaikan dengan data kamu)
GITHUB_USER = "GustanLadinatha"
GITHUB_REPO = "syzo-leech-api"
# Sangat disarankan menggunakan Environment Variable di Vercel untuk TOKEN ini
GITHUB_TOKEN = "PASTE_TOKEN_GITHUB_KAMU_DISINI" 

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    # Menangani pre-flight request dari browser
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"status": "error", "message": "URL tidak ditemukan"}), 400

        target_url = data.get('url')

        # 2. TRIGGER GITHUB ACTIONS
        dispatch_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/dispatches"
        
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "event_type": "start-leech", # Harus sama dengan 'types' di leech.yml
            "client_payload": {
                "url": target_url
            }
        }

        response = requests.post(dispatch_url, json=payload, headers=headers)

        if response.status_code == 204:
            return jsonify({
                "status": "success", 
                "message": "GitHub Worker berhasil dipicu!"
            }), 200
        else:
            return jsonify({
                "status": "error", 
                "message": f"GitHub API Error: {response.text}"
            }), response.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Standar Vercel Serverless
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)
