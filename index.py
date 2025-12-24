from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Mengizinkan koneksi dari website kamu ke Vercel
CORS(app)

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "No URL provided"}), 400
            
        url = data.get('url')
        
        # --- KONFIGURASI GITHUB ---
        # Ganti dengan Token asli kamu
        TOKEN = os.getenv("GH_TOKEN")
        REPO = "GustanLadinatha/syzo-leech-api"
        
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        payload = {
            "event_type": "start-leech",
            "client_payload": {"url": url}
        }
        
        # Kirim perintah ke GitHub
        gh_res = requests.post(
            f"https://api.github.com/repos/{REPO}/dispatches",
            json=payload,
            headers=headers
        )
        
        if gh_res.status_code == 204:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": gh_res.text}), gh_res.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Wajib untuk Vercel
def handler(event, context):
    return app(event, context)
