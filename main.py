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
ZENROWS_API_KEY = os.getenv("ZENROWS_SECRET_KEY")
WHATSAPP_LINK_PATTERN = r"(https?://chat\.whatsapp\.com/[A-Za-z0-9]{20,24})"

def start_fake_server():
    class DummyHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot is perfectly running on Render!")
        def log_message(self, format, *args): return
    port = int(os.environ.get("PORT", 10000))
    server = http.server.HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

def fetch_zenrows_get(url, query_params):
    return requests.get(url, params=query_params, timeout=180)

async def colab_cloud_autopilot_submit(group_link: str):
    if not BOT_TOKEN or not ZENROWS_API_KEY:
        return None, "❌ एरर: गुप्त तिजोरी में टोकन सेट नहीं हैं।"
        
    zenrows_gateway = "https://zenrows.com"
    target_url = "https://groupsor.link"
    
    js_actions = [
        {"wait_for": "input[placeholder*='WhatsApp']"},
        {"fill": ["input[placeholder*='WhatsApp']", group_link]},
        
        # ड्रापडाउन सेलेक्ट करने का बिल्कुल सटीक मॉडर्न तरीका
        {"evaluate": """
            let dropdowns = document.querySelectorAll("select");
            if(dropdowns.length >= 3) {
                dropdowns[0].value = "4"; 
                dropdowns[0].dispatchEvent(new Event('change', { bubbles: true }));
                
                dropdowns[1].value = "102"; 
                dropdowns[1].dispatchEvent(new Event('change', { bubbles: true }));
                
                dropdowns[2].value = "45"; 
                dropdowns[2].dispatchEvent(new Event('change', { bubbles: true }));
            }
        """},
        {"wait": 2000},
        {"click": "button[type='submit'], input[type='submit'], .btn-success"},
        {"wait": 12000}
    ]
    
    # 🌟 1 IP प्रति दिन की लिमिट तोड़ने के लिए रेसिडेंशियल प्रॉक्सी कॉन्फ़िगरेशन
    params = {
        "apikey": ZENROWS_API_KEY,
        "url": target_url,
        "js_render": "true",
        "antibot": "true",           # 🛡️ क्लाउडफ्लेयर 'Verifying...' को बायपास करने के लिए
        "premium_proxy": "true",     
        "proxy_country": "in",       # 🇮🇳 शुद्ध भारतीय फ्रेश IP के लिए
        "js_instructions": json.dumps(js_actions),  
        "screenshot": "true",        # 📸 लाइव सबूत देखने के लिए स्क्रीनशॉट ऑन
        "window_width": "1920",
        "window_height": "1080"
    }
    
    try:
        response = await asyncio.to_thread(fetch_zenrows_get, zenrows_gateway, params)
        content_type = response.headers.get('Content-Type', '')
        
        if response.status_code == 200 and 'image' in content_type:
            return response.content, "📸 फॉर्म ऑटो-सबमिशन का लाइव स्क्रीनशॉट नीचे देखें!"
        else:
            res_text = response.text
            if "already" in res_text.lower() or "exist" in res_text.lower():
                return None, "🛑 वेबसाइट अलर्ट: यह आईपी लिमिट या पुराना लिंक होने के कारण रिजेक्ट हुआ।"
            return None, f"🛑 सबमिशन प्रोसेस अधूरा रहा (Code: {response.status_code})"
    except Exception as e:
        return None, f"❌ एपीआई कनेक्शन एरर: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 क्लाउडफ्लेयर फिक्स बोट ऑनलाइन है! अपना WhatsApp लिंक भेजें।")

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # लिंक के पीछे के फालतू ट्रैकिंग कोड्स को ऑटोमैटिकली साफ़ करना
    raw_text = update.message.text
    m = re.search(WHATSAPP_LINK_PATTERN, raw_text)
    
    if m:
        clean_url = m.group(1) # केवल शुद्ध व्हाट्सएप इनविटेशन लिंक निकालेगा
        status_msg = await update.message.reply_text("📥 लिंक मिल गया! क्लाउडफ्लेयर बाईपास करके फ्रेश भारतीय IP से सबमिट किया जा रहा है... कृपया 45 सेकंड रुकें...")
        
        img_bytes, text_response = await colab_cloud_autopilot_submit(clean_url)
        try: await status_msg.delete()  
        except: pass
        
        if img_bytes:
            photo_file = io.BytesIO(img_bytes)
            photo_file.name = "live_bypass.png"
            try: await update.message.reply_photo(photo=photo_file, caption=text_response)
            except Exception:
                photo_file.seek(0)
                await update.message.reply_document(document=photo_file, filename="live_bypass.png", caption=text_response)
        else:
            await update.message.reply_text(text_response)
    else:
        await update.message.reply_text("❌ कृपया एक सही व्हाट्सएप ग्रुप लिंक भेजें।")

def main():
    if not BOT_TOKEN: return
    threading.Thread(target=start_fake_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).connect_timeout(60).read_timeout(60).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    print("🚀 BYPASS BOT IS RUNNING SUCCESSFULLY!")
    app.run_polling()

if __name__ == "__main__":
    main()
