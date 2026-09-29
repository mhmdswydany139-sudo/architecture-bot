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
        return "الموقع يعمل بنجاح!"

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
    show_main_menu(uid)

def show_main_menu(uid):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_free = types.InlineKeyboardButton("📚 الأقسام الهندسية المجانية", callback_data="free_sections")
    btn_paid = types.InlineKeyboardButton("🔒 مادة الثقافة العربية (مغلق - يتطلب تفعيل)", callback_data="paid_section")
    btn_gpa = types.InlineKeyboardButton("💾 تحميل حاسبة المعدل GPA", callback_data="download_gpa")
    markup.add(btn_free, btn_paid, btn_gpa)
    
    student_bot.send_message(
        uid, 
        "🏛️ أهلاً بك في موسوعة العمارة الشاملة!\n\nيمكنك الآن تصفح الأقسام المجانية مباشرة، أو طلب تفعيل المواد المخصصة عبر الأزرار أدناه:", 
        reply_markup=markup
    )

@student_bot.callback_query_handler(func=lambda call: call.data in ["free_sections", "paid_section", "download_gpa"])
def handle_menu_navigation(call):
    uid = call.message.chat.id
    
    if call.data == "free_sections":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة", callback_data="main_menu")
        markup.add(btn_back)
        student_bot.edit_message_text(
            "📂 **الأقسام المجانية المتاحة للمطالعة:**\n\n1️⃣ نظريات العمارة وتاريخها\n2️⃣ التصميم المعماري والتخطيط\n3️⃣ مواد البناء والمواصفات الفنية\n\n*ملاحظة: جميع ملفات هذه الأقسام مفتوحة ومتاحة للجميع مجاناً!*",
            chat_id=uid,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
        
    elif call.data == "download_gpa":
        try:
            with open("calculator.zip", "rb") as file:
                student_bot.send_document(uid, file, caption="💾 تفضل، ملف حاسبة المعدل التراكمي المجهز مجاناً بصيغة ZIP.")
        except:
            student_bot.send_message(uid, "❌ عذراً، ملف الحاسبة غير متوفر حالياً على السيرفر.")
            
    elif call.data == "paid_section":
        try:
            status = student_bot.get_chat_member(CHANNEL_ID, uid).status
            if status in ['member', 'administrator', 'creator']:
                student_bot.send_message(uid, "🔓 مادة (ثقافة عربية) مفعّلة لديك مسبقاً! يمكنك تصفح الملفات داخل القناة الرسمية.")
                return
        except:
            pass
            
        msg = student_bot.send_message(uid, "📝 لتفعيل مادة (الثقافة العربية) والولوج للقناة السحابية، يرجى إدخال رقمك الجامعي أولاً:")
        student_bot.register_next_step_handler(msg, save_uni_id)

def save_uni_id(message):
    uid = message.from_user.id
    uni_id = message.text.strip()
    msg = student_bot.send_message(uid, "🔒 اختر كلمة مرور خاصة بحسابك لحماية بياناتك الأكاديمية:")
    student_bot.register_next_step_handler(msg, save_password, uni_id)

def save_password(message, uni_id):
    uid = message.from_user.id
    password = message.text.strip()
    msg = student_bot.send_message(uid, "💵 الرجاء إدخال رقم عملية تحويل شام كاش المرجعي للتحقق من قِبل الإدارة وتفعيل المادة:")
    student_bot.register_next_step_handler(msg, handle_payment, uni_id, password)
def handle_payment(message, uni_id, password):
    uid = message.from_user.id
    receipt = message.text.strip()

    if receipt in pending_receipts:
        student_bot.send_message(uid, "❌ خطأ: رقم عملية شام كاش هذه تحت المراجعة حالياً! تم إلغاء الطلب تلقائياً.")
        return

    pending_receipts.add(receipt)

    markup = types.InlineKeyboardMarkup()
    btn_app = types.InlineKeyboardButton("✅ موافقة وتفعيل المادة", callback_data=f"acc_{uid}_{uni_id}_{password}")
    btn_rej = types.InlineKeyboardButton("❌ رفض الطلب", callback_data=f"den_{uid}")
    markup.row(btn_app, btn_rej)

    text = f"🔔 طلب تفعيل مادة مدفوعة جديد:\n\n👤 آيدي الطالب: {uid}\n🎓 الرقم الجامعي: {uni_id}\n🔑 الباسورد: {password}\n💵 رقم الحوالة: {receipt}"
    admin_bot.send_message(MY_PERSONAL_ID, text, reply_markup=markup)
    student_bot.send_message(uid, "⏳ تم إرسال طلب التفعيل بنجاح. يرجى الانتظار لحين مراجعة الحوالة يدوياً من قِبل الإدارة.")

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
            
            database_text = f"PAID_USER_LOG\nID:{target_uid}\nUNI:{uni_id}\nPWD:{password}"
            student_bot.send_message(CHANNEL_ID, database_text)
            
            student_bot.send_message(target_uid, f"🎉 مبارك! تمت مطابقة حوالتك وتفعيل مادة (الثقافة العربية) بنجاح.\n\nرابط الانضمام للقناة السحابية المحمية وتحميل الملفات:\n{link}")
            admin_bot.edit_message_text(f"✅ تم قبول الطالب {target_uid} وتفعيل المادة له بنجاح.", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
            
        except Exception as e:
            admin_bot.answer_callback_query(call.id, f"❌ خطأ برمجي: {str(e)}")
            
    elif action == "den":
        try:
            student_bot.send_message(target_uid, "❌ نعتذر منك، تم رفض طلب التفعيل لأن رقم عملية شام كاش غير مطابق لكشف الحساب.")
            admin_bot.edit_message_text(f"❌ تم رفض طلب الطالب {target_uid} وإخطاره فوراً.", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
        except:
            pass

@student_bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def handle_back_to_menu(call):
    uid = call.message.chat.id
    student_bot.delete_message(uid, call.message.message_id)
    show_main_menu(uid)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
