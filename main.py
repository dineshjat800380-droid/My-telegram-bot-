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

# 🛠️ रेंडर के पोर्ट टाइमआउट को धोखा देने के लिए नकली वेब सर्वर फिक्स
def start_fake_server():
    class DummyHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot is perfectly running!")
        def log_message(self, format, *args):
            return  # लॉग्स को साफ़ रखने के लिए
            
    port = int(os.environ.get("PORT", 10000))  # रेंडर का डिफ़ॉल्ट पोर्ट
    server = http.server.HTTPServer(("0.0.0.0", port), DummyHandler)
    print(f"⚓ Fake Server triggered successfully on port {port} for Render stability!")
    server.serve_forever()

def fetch_zenrows_get(url, query_params):
    return requests.get(url, params=query_params, timeout=180)

async def colab_cloud_autopilot_submit(group_link: str):
    if not BOT_TOKEN or not ZENROWS_API_KEY:
        return None, "❌ एरर: गुप्त तिजोरी में टोकन सेट नहीं हैं।"
    zenrows_gateway = "https://zenrows.com"
    target_url = "https://groupsor.link"
    
    js_actions = [
        {"wait_for": "input[name='link']"},
        {"fill": ["input[name='link']", group_link]},
        {"select_option": ["select[name='cate']", "4"]},
        {"select_option": ["select[name='country']", "102"]},
        {"select_option": ["select[name='language']", "45"]},
        {"wait": 2000},
        {"click": "input[type='submit'], .btn-success"},
        {"wait": 10000}
    ]
    params = {
        "apikey": ZENROWS_API_KEY,
        "url": target_url,
        "js_render": "true",
        "premium_proxy": "true",
        "js_instructions": json.dumps(js_actions),  
        "screenshot": "true",
        "window_width": "1920",
        "window_height": "1080"
    }
    try:
        response = await asyncio.to_thread(fetch_zenrows_get, zenrows_gateway, params)
        content_type = response.headers.get('Content-Type', '')
        if response.status_code == 200 and 'image' in content_type:
            return response.content, "✅ बधाई हो! फॉर्म सबमिशन प्रोसेस पूरा हुआ! नीचे लाइव फोटो देखें।"
        else:
            res_text = response.text
            if "already" in res_text.lower() or "exist" in res_text.lower():
                return None, "🛑 वेबसाइट अलर्ट: यह व्हाट्सएप ग्रुप लिंक पहले से मौजूद है!"
            return None, f"🛑 सबमिशन प्रोसेस अधूरा रहा (Code: {response.status_code})"
    except Exception as e:
        return None, f"❌ एपीआई कनेक्शन एरर: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 बिल्कुल सुरक्षित 100% फ्री बот ऑनलाइन है! व्हाट्सएप लिंक भेजें।")

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = re.search(WHATSAPP_LINK_PATTERN, update.message.text)
    if m:
        status_msg = await update.message.reply_text("📥 लिंक मिल गया! प्रोसेस चालू है... कृपया प्रतीक्षा करें...")
        img_bytes, text_response = await colab_cloud_autopilot_submit(m.group(1))
        try: await status_msg.delete()  
        except: pass
        if img_bytes:
            photo_file = io.BytesIO(img_bytes)
            photo_file.name = "result.png"
            try: await update.message.reply_photo(photo=photo_file, caption=text_response)
            except Exception:
                photo_file.seek(0)
                await update.message.reply_document(document=photo_file, filename="result.png", caption=text_response)
        else:
            await update.message.reply_text(text_response)
    else:
        await update.message.reply_text("❌ कृपया एक सही व्हाट्सएप ग्रुप लिंक भेजें।")

def main():
    if not BOT_TOKEN:
        return
    # 🌟 बैकग्राउंड थ्रेड में नकली सर्वर चालू करना ताकि रेंडर इसे ब्लॉक न करे
    threading.Thread(target=start_fake_server, daemon=True).start()
    
    app = Application.builder().token(BOT_TOKEN).connect_timeout(60).read_timeout(60).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    print("🚀 SAFE FREE BOT IS RUNNING ON RENDER WEB SERVICE!")
    app.run_polling()

if __name__ == "__main__":
    main()
