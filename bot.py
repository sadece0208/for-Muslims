import os
import threading
from flask import Flask

app = Flask(__name__)


@app.route("/")
def health_check():
  return "Bot ishlamoqda!", 200


def run_http():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_http, daemon=True).start()
import logging
import random
from datetime import time
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "8897067870:AAHqxWapVQO1xQFc0RCIIxvTK148-vDXxWE"
TIMEZONE = pytz.timezone("Asia/Tashkent")

# 1. Turli xil Salovatlar va Zikrlar
SALAVATLAR = [
    "Allohumma solli 'ala Muhammadin va 'ala ali Muhammad.",
    "Sollallohu 'alayhi va sallam.",
    "Allohumma solli 'ala Sayyidina Muhammadin nabiyyil ummiyyi va 'ala alihi va sohbihi va sallim.",
    "Astag'firullohallazi la ilaha illa huval Hayyul Qoyyum va atubu ilayh.",
    "Allohumma solli 'ala Muhammadiv-va 'ala ali Muhammad, kama sollayta 'ala Ibrohima va 'ala ali Ibrohim.",
    "Subhonallohi va bihamdihi, Subhonallohil 'Azim.",
    "La havla va la quvvata illa billahil 'Aliyyil 'Azim.",
    "La ilaha illallohu vahdahu la sharika lah, lahul mulku va lahul hamdu va huva 'ala kulli shay'in qodir."
]

# 2. Payg'ambarimiz (s.a.v.) ning sunnatlari
SUNNATLAR = [
    "O'ng qo'l bilan taom yeyish va suvni 3 bo'lib ichish.",
    "Kiyinish va poyabzal kiyishni o'ng tomondan, yechishni esa chap tomondan boshlash.",
    "Insonlarga tabassum qilish — bu ham bir sadaqadir.",
    "Uxlashdan oldin 'Oyatul Kursiy'ni o'qish va tahorat bilan yotish.",
    "Biron joyga kirganda va chiqqanda salom berish.",
    "Aksurganda 'Alhamdulillah' deyish.",
    "Misvok ishlatish yoki tishlarni doim ozoda tutish.",
    "Taomdan oldin va keyin qo'llarni yuvish.",
    "G'azab kelganda 'A'uzu billahi minash-shaytonir-rojim' deb jim bo'lish."
]

# 3. Qur'on yodlash va o'qish topshiriqlari
QURON_TOPSHIRIQ = [
    "Bugun 'Fotiha' surasining ma'nolarini o'rganing va tammufaqqur qiling.",
    "Bugun 'Ixlos', 'Falaq', 'Nas' suralarini tajvid bilan takrorlang.",
    "Bugun 'Oyatul Kursiy'ni yod oling yoki tajvid bilan qayta o'qing.",
    "Bugun Qur'oni Karimdan kamida 1 bet (yoki 1 bet tarjimasini) o'qing.",
    "Bugun 'Mulk' surasini eshitib, birgalikda o'qishga harakat qiling.",
    "Bugun 'Yasin' surasini tinglang yoki o'qing.",
    "Bugun o'zingiz yod olgan kichik suralarni namozda ixlos bilan o'qing."
]

# 4. Musulmon kishining hayotiy farz va qoidalari (Qur'on va Sunnatdan)
HAYOTIY_QOIDALAR = [
    "Ota-onaga yaxshilik qilish — Allohga ibodatdan keyingi eng muhim burchdir.",
    "Rizqni faqat HALOL yo'l bilan toping, harom luqmadan va ribo (suxmaxo'rlik)dan saqlaning.",
    "Sadaqa va ehson qilib turing. Sadaqa molni kamaytirmaydi, baraka keltiradi.",
    "Rostg'oy bo me'yoriy munosabatda bo'ling, yolg'on va g'iybatdan tilingizni asrang.",
    "Qarindoshlik rishtalarini (Silai rahm) bog'lang, xabar olib turing.",
    "Amanatga xiyonat qilmang, bergan va'dangiz ustida turing.",
    "Kechirimli va sabrli bo'ling. Alloh sabr qiluvchilar bilan birgadir."
]

PRAYERS = {
    "bomdod": {"name": "Bamdod", "time": time(5, 30, tzinfo=TIMEZONE)},
    "peshin": {"name": "Peshin", "time": time(13, 0, tzinfo=TIMEZONE)},
    "asr": {"name": "Asr", "time": time(16, 30, tzinfo=TIMEZONE)},
    "shom": {"name": "Shom", "time": time(18, 45, tzinfo=TIMEZONE)},
    "xufton": {"name": "Xufton", "time": time(20, 30, tzinfo=TIMEZONE)},
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    
    if context.job_queue:
        jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        if jobs:
            for job in jobs:
                job.schedule_removal()

    intro_text = (
        "Assalomu alaykum va rohmatullohi va barokatuh!\n\n"
        "🌙 **Musulmonning komil hayot dasturi botiga xush kelibsiz!**\n\n"
        "📌 **Bot har kuni va har haftada sizga eslatib turadi:**\n"
        "• **Har 30 minutda:** Turli salovatlar, Sunnat amallar, Qur'on yodlash va hayotiy islomiy qoidalar.\n"
        "• **Har hafta (Juma kuni):** Ehson, Zakot hisob-kitobi va Juma amallari.\n"
        "• **Kunlik Namozlar:** Namoz vaqti va 30 daqiqadan keyin Allohga qasam ichdirib tekshirish.\n"
        "• **Kitob Mutolaasi:** Kunlik ilmiy va islomiy kitoblar o'qish eslatmasi.\n\n"
        "⚡️ *Birinchi kompleks eslatma yuborilmoqda...*"
    )
    
    await update.message.reply_text(intro_text, parse_mode="Markdown")

    # Birinchi xabar
    await send_comprehensive_reminder(context, chat_id)

    # 1. Har 30 daqiqada takrorlanuvchi taymer
    if context.job_queue:
        context.job_queue.run_repeating(
            send_30min_job,
            interval=1800,
            first=1800,
            chat_id=chat_id,
            name=str(chat_id)
        )

        # 2. Kunlik namoz vaqtlari
        for key, info in PRAYERS.items():
            context.job_queue.run_daily(
                send_prayer_warning,
                time=info["time"],
                chat_id=chat_id,
                name=str(chat_id),
                data=key
            )

        # 3. Har haftalik JUMA va EHSON/ZAKOT eslatmasi (Juma kuni soat 09:00 da)
        context.job_queue.run_daily(
            send_weekly_ehson_reminder,
            time=time(9, 0, tzinfo=TIMEZONE),
            days=(4,), # 4 = Juma kuni
            chat_id=chat_id,
            name=str(chat_id)
        )

async def send_comprehensive_reminder(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    salavat = random.choice(SALAVATLAR)
    sunnat = random.choice(SUNNATLAR)
    quron = random.choice(QURON_TOPSHIRIQ)
    qoida = random.choice(HAYOTIY_QOIDALAR)
    
    msg = (
        f"📿 **Salovat va Zikr:**\n`{salavat}`\n\n"
        f"🌱 **Bugungi Sunnat amal:**\n• {sunnat}\n\n"
        f"📖 **Qur'on yodlash va Tilovat:**\n• {quron}\n\n"
        f"💡 **Musulmonning hayotiy qoidasi:**\n• {qoida}\n\n"
        f"📚 **Kitob eslatmasi:** Bugun kamida 5-10 bet ilmiy-ma'rifiy kitob o'qishni unutmang!"
    )
    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

async def send_30min_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await send_comprehensive_reminder(context, job.chat_id)

async def send_weekly_ehson_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    msg = (
        "🕌 **JUMA AYYOMI MUBORAK BO'LSIN!**\n\n"
        "💰 **Haftalik Ehson va Zakot eslatmasi:**\n"
        "• Bugun muhtojlarga, yetimlarga yoki yaqinlaringizga imkon darajasida **ehson va sadaqa** qiling.\n"
        "• Agar mulingiz nisobga (zakot miqdoriga) yetgan bo'lsa, **Zakotingizni** hisoblab, o'z egalariga bering!\n\n"
        "✨ **Juma kunining sunnatlari:**\n"
        "1. G'usl qilish va xushbo'ylanib masjidga borish.\n"
        "2. 'Kahf' surasini o'qish.\n"
        "3. Payg'ambarimizga ko'p salovat aytish."
    )
    await context.bot.send_message(chat_id=job.chat_id, text=msg, parse_mode="Markdown")

async def send_prayer_warning(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    key = job.data
    prayer_name = PRAYERS[key]["name"]

    keyboard = [[InlineKeyboardButton("Xo'p, hozir o'qiyman", callback_data=f"read_{key}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = f"🚨 **{prayer_name} namozining vaqti bo'ldi!**\nShoshiling, namoz vaqti o'tib ketmasin!"
    
    await context.bot.send_message(
        chat_id=job.chat_id, 
        text=msg, 
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    if context.job_queue:
        context.job_queue.run_once(
            send_prayer_check,
            when=1800, # 30 daqiqadan keyin tekshiradi
            chat_id=job.chat_id,
            data=key
        )

async def send_prayer_check(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    key = job.data
    prayer_name = PRAYERS[key]["name"]

    keyboard = [
        [
            InlineKeyboardButton("Ha, Allohga qasam o'qidim", callback_data=f"confirm_yes_{key}"),
            InlineKeyboardButton("Yo'q, o'qimadim", callback_data=f"confirm_no_{key}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        f"⚠️ **{prayer_name} namozidan 30 daqiqa o'tdi!**\n\n"
        f"{prayer_name} namozingizni o'qidingizmi? Alloh uchun qasam iching-chi, o'qidingizmi yoki yo'q?"
    )
    await context.bot.send_message(chat_id=job.chat_id, text=msg, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("read_"):
        await query.edit_message_text("Barakalloh! Darhol tahorat olib, namozni ado eting.")
    
    elif data.startswith("confirm_yes_"):
        await query.edit_message_text("✅ Alloh ibodatingizni qabul qilsin va doimiy qilsin!")

    elif data.startswith("confirm_no_"):
        strict_msg = (
            "❌ **Sizni nima chalg'ityapti?!**\n\n"
            "Dunyo ishlari o'limingizdan keyin to'xtaydi, lekin namozsiz o'tsangiz javobi juda og'ir bo'ladi! "
            "Turing, darhol tahorat oling va qazo qilmay namozingizni o'qing!"
        )
        await query.edit_message_text(strict_msg, parse_mode="Markdown")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot muvaffaqiyatli ishga tushdi...")
    application.run_polling()

if __name__ == "__main__":
    main()
