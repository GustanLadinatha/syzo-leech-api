from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

TOKEN = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-5089072043" # Gunakan ID yang berawalan -100 jika itu Supergroup

@app.route('/')
def home():
    return "Syzo API is Online on Vercel"

@app.route('/leech', methods=['POST'])
def leech():
    try:
        data = request.get_json(silent=True) # Pakai silent=True agar tidak langsung crash jika JSON kosong
        print(f"Data diterima: {data}") # Ini akan muncul di log Vercel
        
        if not data:
            return jsonify({"status": "Error", "msg": "Request body kosong"}), 400
            
        # Ambil URL, coba beberapa kemungkinan kunci (url atau link)
        url_target = data.get('url') or data.get('link')
        
        if not url_target:
            return jsonify({"status": "Error", "msg": "Mana link-nya? Kunci 'url' tidak ada"}), 400
            
        pesan = f"🚀 *New Leech Request*\n\nTarget: {url_target}"
        
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(api_url, json={
    "chat_id": CHAT_ID, 
    "text": pesan, 
    "parse_mode": "Markdown"
})
        
        return jsonify({"status": "Success", "msg": "Terkirim!"}), 200
        
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True)



