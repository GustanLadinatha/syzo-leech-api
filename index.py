from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time  # <-- PASTIKAN BARIS INI ADA

app = Flask(__name__)
CORS(app)

TOKEN = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-5089072043"

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    if request.method == 'OPTIONS':
        return jsonify({"status": "OK"}), 200
    try:
        data = request.get_json(silent=True)
        url_target = data.get('url')
        
        # Format waktu untuk laporan
        waktu_sekarang = time.strftime('%H:%M:%S')
        
        # Gunakan f-string untuk pesan. 
        # Kita tidak pakai Markdown dulu agar aman dari error parsing link SourceForge
        pesan = (
            "🚀 *New Leech Request*\n\n"
            f"Target: {url_target}\n"
            f"Clock: {waktu_sekarang} WIB"
        )
        
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(api_url, json={
            "chat_id": CHAT_ID, 
            "text": pesan,
            "parse_mode": "Markdown" # Pakai Markdown biasa saja
        }, timeout=15)
        
        if r.ok:
            return jsonify({"status": "Success", "msg": "Terkirim!"}), 200
        else:
            # Jika gagal karena Markdown, kirim ulang sebagai teks biasa
            requests.post(api_url, json={"chat_id": CHAT_ID, "text": pesan})
            return jsonify({"status": "Success", "msg": "Terkirim (Plain Text)!"}), 200
            
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500
