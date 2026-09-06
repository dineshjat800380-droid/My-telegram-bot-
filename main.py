import asyncio
import re
import io
import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 🛠️ सुरक्षा के लिए आपका टोकन और ZenRows API Key
BOT_TOKEN = "8943148389:AAFeddureNMhaYUXFARXSMiVnSkcHUyRZX8"
ZENROWS_API_KEY = "d5772fce840c180018c4cf284749e246cad1012d"
WHATSAPP_LINK_PATTERN = r"(https?://chat\.whatsapp\.com/[A-Za-z0-9]{20,24})"

def fetch_zenrows_get(url, query_params):
    return requests.get(url, params=query_params, timeout=180)

async def colab_cloud_autopilot_submit(group_link: str):
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
                return None, "🛑 वेबसाइट अलर्ट: यह व्हाट्सएप ग्रुप लिंक इस वेबसाइट पर पहले से ही मौजूद है!"
            return None, f"🛑 सबमिशन प्रोसेस अधूरा रहा (Code: {response.status_code})\nविवरण: {res_text[:100]}"
    except Exception as e:
        return None, f"❌ एपीआई कनेक्शन एरर: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 बोट ऑनलाइन है! अपना WhatsApp लिंक भेजें।")

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = re.search(WHATSAPP_LINK_PATTERN, update.message.text)
    if m:
        status_msg = await update.message.reply_text("📥 लिंक मिल गया! क्लाउड सर्वर से डेटा प्रोसेस हो रहा है... कृपया प्रतीक्षा करें...")
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
    app = Application.builder().token(BOT_TOKEN).connect_timeout(60).read_timeout(60).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    app.run_polling()

if __name__ == "__main__":
    main()
