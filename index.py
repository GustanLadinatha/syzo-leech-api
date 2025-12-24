from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Baris di bawah ini adalah kunci untuk menghilangkan error merah di console kamu
CORS(app)

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Kirim pemicu ke GitHub Actions
    # Ganti dengan User, Repo, dan Token GitHub kamu yang benar
    github_url = "https://api.github.com/repos/GustanLadinatha/syzo-leech-api/dispatches"
    headers = {
        "Authorization": "Bearer GITHUB_TOKEN_KAMU_DISINI",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "event_type": "start-leech",
        "client_payload": {"url": url}
    }
    
    requests.post(github_url, json=payload, headers=headers)
    
    return jsonify({"status": "success", "message": "GitHub Worker Triggered"}), 200

def handler(event, context):
    return app(event, context)
