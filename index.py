name: Syzo Leech Worker

on:
  repository_dispatch:
    types: [start-leech]

jobs:
  leech-job:
    runs-on: ubuntu-latest
    steps:
      - name: Install Dependencies
        run: sudo apt-get update && sudo apt-get install -y jq wget curl

      - name: Download File from SourceForge
        run: |
          URL="${{ github.event.client_payload.url }}"
          # Download dan paksa ambil nama file asli
          wget -q --show-progress --content-disposition "$URL"
          
          # AMANKAN NAMA FILE: Buang karakter ?viasf=1 dan spasi
          RAW_NAME=$(ls -p | grep -v / | grep -v "leech.yml" | head -n 1)
          CLEAN_NAME=$(echo "$RAW_NAME" | cut -d'?' -f1 | tr ' ' '_')
          
          if [ "$RAW_NAME" != "$CLEAN_NAME" ]; then
            mv "$RAW_NAME" "$CLEAN_NAME"
          fi
          
          echo "FILENAME=$CLEAN_NAME" >> $GITHUB_ENV

      - name: Upload to GoFile
        run: |
          # Ambil server upload
          SERVER=$(curl -s https://api.gofile.io/getServer | jq -r '.data.server // "store1"')
          
          # Upload file yang sudah bersih namanya
          curl -v -F "file=@${{ env.FILENAME }}" "https://${SERVER}.gofile.io/uploadFile" > response.json
          
          # Ambil link download
          DOWNLOAD_LINK=$(jq -r '.data.downloadPage // empty' response.json)
          
          if [ "$DOWNLOAD_LINK" != "" ] && [ "$DOWNLOAD_LINK" != "null" ]; then
            echo "DOWNLOAD_URL=$DOWNLOAD_LINK" >> $GITHUB_ENV
          else
            echo "Gagal Upload. Respon:"
            cat response.json
            exit 1
          fi

      - name: Notify Telegram (Success)
        if: success()
        run: |
          curl -s -X POST "https://api.telegram.org/bot${{ secrets.TOKEN_BOT }}/sendMessage" \
          -d "chat_id=${{ secrets.CHAT_ID }}&text=✅ Leech Berhasil!%0A%0AFile: ${{ env.FILENAME }}%0AURL: ${{ env.DOWNLOAD_URL }}"
