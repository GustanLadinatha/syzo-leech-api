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
    if request.method == 'OPTIONS':
        return jsonify({"status": "OK"}), 200
        
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "Error", "msg": "Request body kosong"}), 400
            
        url_target = data.get('url')
        if not url_target:
            return jsonify({"status": "Error", "msg": "Kunci 'url' tidak ditemukan"}), 400
            
        # Kita hapus simbol bintang (*) dan ganti format pesan agar aman dari error parsing
        pesan = f"🚀 New Leech Request\n\nTarget: {url_target}"
        
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        
        # PENTING: Hapus "parse_mode": "Markdown" agar link tidak dianggap kode yang rusak
        r = requests.post(api_url, json={
            "chat_id": CHAT_ID, 
            "text": pesan
        }, timeout=15)
        
        if r.ok:
            return jsonify({"status": "Success", "msg": "Terkirim!"}), 200
        else:
            return jsonify({"status": "Error", "msg": f"Telegram Error: {r.text}"}), r.status_code
            
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)

# Contoh pesan yang lebih informatif
pesan = (
    "✅ *Leech Request Berhasil*\n\n"
    f"🌐 *Source:* SourceForge\n"
    f"🔗 *Link:* [Klik di Sini]({url_target})\n"
    f"⏰ *Waktu:* {time.strftime('%H:%M:%S')} WIB"
)
# Jika pakai format [Teks](Link), pastikan nyalakan lagi parse_mode="Markdown"
