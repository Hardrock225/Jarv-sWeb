import os
from flask import Flask, render_template_string, request, jsonify, send_file
from openai import OpenAI
from dotenv import load_dotenv
from gtts import gTTS
import io

load_dotenv()

# OpenAI istemcisini başlat (API Key ortam değişkeninden alınır)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# HTML şablonunu doğrudan yükle
with open('templates/index.html', 'r', encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get('message', '')
    
    if not user_message:
        return jsonify({"reply": "Sizi duyamadım efendim."})

    # Tablete özel veya temel komut kontrolleri
    if "saat kaç" in user_message.lower():
        from datetime import datetime
        reply = f"Şu an saat {datetime.now().strftime('%H:%M')}, efendim."
    elif "tarih" in user_message.lower() or "bugün günlerden ne" in user_message.lower():
        from datetime import datetime
        reply = f"Bugün {datetime.now().strftime('%d %B %Y')}, efendim."
    else:
        # OpenAI GPT Modeli ile akıllı sohbet cevabı
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Sen Iron Man filmindeki yapay zeka JARVIS'sin. Kullanıcıya her zaman 'efendim' diye hitap et. Çok zeki, esprili, sadık ve yardımsever ol. Karşındaki kişi senin yaratıcın Tony Stark gibi davranabilir. Cevaplarını net ve seslendirmeye uygun şekilde kısa tut."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = "Üzgünüm efendim, merkez sunucularıma bağlanırken bir sorun oluştu."

    return jsonify({"reply": reply})

@app.route('/speech')
def speech():
    text = request.args.get('text', '')
    if not text:
        return "No text provided", 400
        
    tts = gTTS(text=text, lang='tr')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return send_file(fp, mimetype='audio/mp3')

if __name__ == '__main__':
    # Render veya yerel çalıştırma port ayarı
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
