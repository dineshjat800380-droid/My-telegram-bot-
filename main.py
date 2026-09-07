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

# 🌟 रेंडर पर बोट को चालू रखने के लिए आपका आजमाया हुआ नकली वेब सर्वर
def start_fake_server():
    class DummyHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"10x Free Proxy Rotating Autopilot Engine is Active!")
        def log_message(self, format, *args): return
            
    port = int(os.environ.get("PORT", 10000))
    server = http.server.HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# 🌟 प्रॉक्सी काउंट को ट्रैक करने के लिए एक ग्लोबल काउंटर
proxy_counter = 0

def submit_via_rotating_proxy(group_link: str):
    global proxy_counter
    submit_url = "https://groupsor.link"
    
    form_data = {
        "link": group_link,
        "cate": "4",
        "country": "102",
        "language": "45"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://groupsor.link"
    }

    # 🛠️ आपके स्क्रीनशॉट से निकाली गई बिल्कुल असली सभी 10 मुफ्त प्रॉक्सी की लिस्ट
    proxy_pool = [
        "http://31.59.20",   # 1. UK (London)
        "http://45.38.107",   # 2. Spain (Madrid)
        "http://198.105.121", # 3. US (Los Angeles)
        "http://64.137.96",   # 4. US (Piscataway)
        "http://198.23.243",  # 5. Poland (Warsaw)
        "http://38.154.185",   # 6. Japan (Tokyo)
        "http://84.247.60",  # 7. US (Los Angeles)
        "http://142.111.67", # 8. Germany (Frankfurt)
        "http://191.26.254", # 9. Fresh IP 1
        "http://31.58.9"       # 10. Fresh IP 2
    ]

    # 🌟 जादू: हर बार नया लिंक आने पर लिस्ट में से अगली प्रॉक्सी चुनना
    current_proxy = proxy_pool[proxy_counter % len(proxy_pool)]
    # अगले लिंक के लिए काउंटर को बढ़ा देना
    proxy_counter += 1

    my_proxies = {
        "http": current_proxy,
        "https": current_proxy
    }

    try:
        # लॉग्स में दिखेगा कि अभी कौन सी प्रॉक्सी यूज़ हो रही है
        hidden_ip = current_proxy.split('@')[-1]
        print(f"📡 रोटेटिंग इंजन: इस बार फ्रेश IP ({hidden_ip}) से सबमिट किया जा रहा है...")
        
        response = requests.post(submit_url, data=form_data, headers=headers, proxies=my_proxies, timeout=25)
        res_text = response.text
        
        if response.status_code == 200:
            if "already" in res_text.lower() or "exist" in res_text.lower():
                return f"🛑 वेबसाइट अलर्ट: यह विशिष्ट लिंक पहले से सबमिट है, लेकिन आपकी प्रॉक्सी (IP: {hidden_ip}) बिल्कुल सही काम कर रही है!"
            elif "success" in res_text.lower() or "added" in res_text.lower() or "submitted" in res_text.lower():
                return f"✅ बधाई हो! फ्रेश प्रॉक्सी IP ({hidden_ip}) का उपयोग करके आपका ग्रुप लिंक सफलतापूर्वक सबमिट हो गया है।"
            else:
                return f"✅ लिंक प्रोसेस हो गया है (प्रॉक्सी IP: {hidden_ip})! कृपया मुख्य वेबसाइट पर जाकर चेक करें।"
        else:
            return f"🛑 वेबसाइट सर्वर ने एरर दी। स्टेटस कोड: {response.status_code}"

    except Exception as e:
        return "❌ इस प्रॉक्सी रूट पर टाइमआउट हुआ, अगले लिंक पर बोट अपने आप ऑटो-स्विच हो जाएगा।"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 10x रोटेटिंग प्रॉक्सी बोट ऑनलाइन है! अपना WhatsApp लिंक भेजें।")

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    m = re.search(WHATSAPP_LINK_PATTERN, raw_text)
    
    if m:
        clean_url = m.group(1)
        status_msg = await update.message.reply_text("📥 लिंक मिल गया! ऑटो-रोटेटिंग प्रॉक्सी से बिल्कुल नया IP सेट किया जा रहा है... कृपया 5 सेकंड रुकें...")
        
        text_response = await asyncio.to_thread(submit_via_free_proxy if 'submit_via_free_proxy' in globals() else submit_via_rotating_proxy, clean_url)
        
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
    print("🚀 AUTOMATIC ROTATING PROXY BOT IS LIVE ON RENDER!")
    app.run_polling()

if __name__ == "__main__":
    main()
