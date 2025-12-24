@app.route('/cancel', methods=['POST', 'OPTIONS'])
def cancel():
    # 1. TANGANI IZIN BROWSER (PENTING!)
    if request.method == 'OPTIONS':
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response, 200

    try:
        data = request.get_json()
        run_id = data.get('run_id')
        file_name = data.get('file_name', 'File')

        if not run_id:
            return jsonify({"status": "Error", "msg": "Run ID tidak ditemukan"}), 400

        # 2. EKSEKUSI PEMBATALAN KE GITHUB
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        cancel_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/actions/runs/{run_id}/cancel"
        gh_resp = requests.post(cancel_url, headers=headers)

        # 3. NOTIFIKASI KE TELEGRAM
        pesan_cancel = (
            "❌ *PROSES DIBATALKAN*\n\n"
            f"📁 File: `{file_name}`\n"
            "⚠️ Status: _Aborted via Web User_"
        )
        requests.post(f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage", json={
            "chat_id": CHAT_ID, 
            "text": pesan_cancel, 
            "parse_mode": "Markdown"
        })

        return jsonify({"status": "Success", "msg": "Worker stopped"}), 200

    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500
