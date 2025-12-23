from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Memberikan izin CORS tambahan via Flask
CORS(app, resources={r"/*": {"origins": "*"}})

TOKEN = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-5089072043"

@app.route('/')
def home():
    return "Syzo API is Online on Vercel"

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    # Menangani permintaan 'cek izin' dari browser
    if request.method == 'OPTIONS':
        return jsonify({"status": "OK"}), 200
        
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({"status": "Error", "msg": "Request body kosong"}), 400
            
        # Pastikan kunci yang diambil adalah 'url' sesuai dengan JS kamu
        url_target = data.get('url')
        
        if not url_target:
            return jsonify({"status": "Error", "msg": "Kunci 'url' tidak ditemukan"}), 400
            
        pesan = f"🚀 *New Leech Request*\n\nTarget: {url_target}"
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        
        # Kirim ke Telegram
        r = requests.post(api_url, json={
            "chat_id": CHAT_ID, 
            "text": pesan, 
            "parse_mode": "Markdown"
        }, timeout=15)
        
        if r.ok:
            return jsonify({"status": "Success", "msg": "Terkirim!"}), 200
        else:
            return jsonify({"status": "Error", "msg": f"Telegram Error: {r.text}"}), r.status_code
            
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
