from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

TOKEN = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-5089072043"

@app.route('/')
def home():
    return "Syzo API is Online on Vercel"

@app.route('/leech', methods=['POST'])
def leech():
    try:
        data = request.json
        url_target = data.get('url', 'No URL')
        pesan = f"🚀 *New Leech Request*\n\nTarget: {url_target}"
        
        # Di Vercel, kita bisa pakai domain resmi tanpa takut diblokir
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        
        r = requests.post(api_url, json={
            "chat_id": CHAT_ID, 
            "text": pesan, 
            "parse_mode": "Markdown"
        }, timeout=10)
        
        return jsonify({"status": "Success", "msg": "Sent!"}) if r.ok else jsonify({"status": "Error", "msg": r.text}), 500
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500