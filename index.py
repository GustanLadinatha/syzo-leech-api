from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Membuka izin akses agar localhost bisa mengirim data ke Vercel
CORS(app, resources={r"/*": {"origins": "*"}})

TOKEN = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-5089072043"

@app.route('/')
def home():
    return "Syzo API is Online on Vercel"

@app.route('/leech', methods=['POST', 'OPTIONS'])
def leech():
    # Menangani 'Preflight Request' dari browser agar tidak CORS Error
    if request.method == 'OPTIONS':
        return jsonify({"status": "OK"}), 200
        
    try:
        data = request.get_json(silent=True)
        print(f"Data diterima: {data}")
        
        if not data:
            return jsonify({"status": "Error", "msg": "Request body kosong"}), 400
            
        url_target = data.get('url') or data.get('link')
        
        if not url_target:
            return jsonify({"status": "Error", "msg": "Kunci 'url' tidak ditemukan"}), 400
            
        pesan = f"🚀 *New Leech Request*\n\nTarget: {url_target}"
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        
        # Proses kirim ke Telegram
        r = requests.post(api_url, json={
            "chat_id": CHAT_ID, 
            "text": pesan, 
            "parse_mode": "Markdown"
        }, timeout=15)
        
        print(f"Respon Telegram: {r.status_code} - {r.text}")

        if r.ok:
            return jsonify({"status": "Success", "msg": "Terkirim!"}), 200
        else:
            return jsonify({"status": "Error", "msg": f"Telegram: {r.text}"}), r.status_code
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "Error", "msg": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
