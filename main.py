import asyncio
import re
import io
import json
import requests
import os
import http.server
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WHATSAPP_LINK_PATTERN = r"(https?://chat\.whatsapp\.com/[A-Za-z0-9]{20,24})"

# 🛠️ रेंडर की स्टेबिलिटी के लिए आपका आजमाया हुआ नकली वेब सर्वर फिक्स
def start_fake_server():
    class DummyHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Free Webshare Proxy Autopilot is Running Successfully!")
        def log_message(self, format, *args): return
            
    port = int(os.environ.get("PORT", 10000))
    server = http.server.HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# 🌟 आपके द्वारा खोजी गई मुफ़्त Webshare प्रॉक्सी के साथ डायरेक्ट फॉर्म सबमिशन
def submit_via_free_proxy(group_link: str):
    submit_url = "https://groupsor.link"
    
    # आपके स्क्रीनशॉट के अनुसार बिल्कुल सटीक फॉर्म डेटा
    form_data = {
        "link": group_link,    # व्हाट्सएप ग्रुप लिंक
        "cate": "4",           # Entertainment / Hindi
        "country": "102",      # India
        "language": "45"       # Hindi
    }
    
    # ब्राउज़र जैसा दिखने के लिए सामान्य हेडर
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://groupsor.link"
    }

    # 🌟 आपका बिल्कुल असली क्रेडेंशियल्स वाला मुफ़्त प्रॉक्सी सेटअप
    my_proxies = {
        "http": "http://midzpdvd:o6gc4q9nch24@p.webshare.io:80/",
        "https": "http://midzpdvd:o6gc4q9nch24@p.webshare.io:80/"
    }

    try:
        print(f"📡 बिल्कुल फ्रेश मुफ़्त प्रॉक्सी IP से डेटा भेजा जा रहा है...")
        # बिना किसी रैम एरर के, प्रॉक्सी के जरिए सीधे वेबसाइट के बैकएंड पर अटैक (POST)
        response = requests.post(submit_url, data=form_data, headers=headers, proxies=my_proxies, timeout=20)
        res_text = response.text
        
        if response.status_code == 200:
            if "already" in res_text.lower() or "exist" in res_text.lower():
                return "🛑 वेबसाइट अलर्ट: यह लिंक इस वेबसाइट पर पहले से ही मौजूद है!"
            elif "success" in res_text.lower() or "added" in res_text.lower() or "submitted" in res_text.lower():
                return "✅ बधाई हो! मुफ़्त प्रॉक्सी IP का उपयोग करके आपका ग्रुप लिंक सफलतापूर्वक सबमिट हो गया है।"
            else:
                return "✅ लिंक भेज दिया गया है! कृपया मुख्य वेबसाइट पर जाकर चेक करें।"
        else:
            return f"🛑 वेबसाइट सर्वर ने एरर दी। स्टेटस कोड: {response.status_code}"

    except Exception as e:
        return f"❌ प्रॉक्सी कनेक्शन एरर (IP limit or timeout): {str(e)[:80]}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 मुफ़्त प्रॉक्सी-फिक्स्ड बोट ऑनलाइन है! अपना WhatsApp लिंक भेजें।")

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    m = re.search(WHATSAPP_LINK_PATTERN, raw_text)
    
    if m:
        clean_url = m.group(1) # ट्रैकिंग कोड्स को ऑटो-क्लिन करना
        status_msg = await update.message.reply_text("📥 लिंक मिल गया! बिल्कुल फ्रेश मुफ़्त प्रॉक्सी IP से डायरेक्ट सबमिट किया जा रहा है...")
        
        # बिना थ्रेड ब्लॉक किए बैकग्राउंड में फंक्शन रन करना (सिर्फ 2 सेकंड में रिजल्ट)
        text_response = await asyncio.to_thread(submit_via_free_proxy, clean_url)
        
        try: await status_msg.delete()  
        except: pass
            
        await update.message.reply_text(text_response)
    else:
        await update.message.reply_text("❌ कृपया एक सही व्हाट्सएप ग्रुप लिंक भेजें।")

def main():
    if not BOT_TOKEN:
        return
    threading.Thread(target=start_fake_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).connect_timeout(30).read_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    print("🚀 PROXY AUTO-POST BOT IS LIVE ON RENDER!")
    app.run_polling()

if __name__ == "__main__":
    main()
