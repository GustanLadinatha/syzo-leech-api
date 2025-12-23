from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Izinkan CORS agar bisa diakses dari localhost:5500
CORS(app)

TOKEN = "8229203638:AAHI-0fu5NGv8kQmUm5ztd81gbOautvJBB4"
CHAT_ID = "-1002447926207" # Pastikan ID Group benar (cek screenshot sukses sebelumnya)

@app.route('/')
def home():
    return "Syzo API is Online on Vercel"

@app.route('/leech', methods=['POST'])
def leech():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "Error", "msg": "No data received"}), 400
            
        url_target = data.get('url', 'No URL')
        pesan = f"🚀 *New Leech Request*\n\nTarget: {url_target}"
        
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        
        # Kirim ke Telegram dengan timeout agar tidak menggantung lama
        r = requests.post(api_url, json={
            "chat_id": CHAT_ID, 
            "text": pesan, 
            "parse_mode": "Markdown"
        }, timeout=15)
        
        if r.ok:
            return jsonify({"status": "Success", "msg": "Sent to Telegram!"}), 200
        else:
            # Jika Telegram menolak (misal chat_id salah), kirim pesan errornya
            return jsonify({"status": "Error", "msg": f"Telegram API: {r.text}"}), r.status_code

    except requests.exceptions.Timeout:
        return jsonify({"status": "Error", "msg": "Koneksi ke Telegram Timeout (Server Sibuk)"}), 504
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

# Penting untuk Vercel
if __name__ == '__main__':
    app.run(debug=True)
