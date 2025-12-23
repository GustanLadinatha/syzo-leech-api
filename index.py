from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

TOKEN = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-1002447926207" # Gunakan ID yang berawalan -100 jika itu Supergroup

@app.route('/')
def home():
    return "Syzo API is Online on Vercel"

@app.route('/leech', methods=['POST'])
def leech():
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({"status": "Error", "msg": "URL tidak ditemukan dalam request"}), 400
            
        url_target = data.get('url')
        pesan = f"🚀 *New Leech Request*\n\nTarget: {url_target}"
        
        # Gunakan session untuk koneksi yang lebih stabil
        session = requests.Session()
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        
        # Coba kirim dengan timeout lebih panjang (20 detik)
        r = session.post(api_url, json={
            "chat_id": CHAT_ID, 
            "text": pesan, 
            "parse_mode": "Markdown"
        }, timeout=20)
        
        if r.ok:
            return jsonify({"status": "Success", "msg": "Berhasil terkirim!"}), 200
        else:
            return jsonify({"status": "Error", "msg": f"Telegram Reject: {r.text}"}), r.status_code

    except requests.exceptions.Timeout:
        return jsonify({"status": "Error", "msg": "Server Vercel tidak bisa menjangkau Telegram (Timeout)"}), 504
    except Exception as e:
        return jsonify({"status": "Error", "msg": f"Crash: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
