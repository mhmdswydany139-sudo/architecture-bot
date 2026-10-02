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
    return "Local Storage Bridge Active"

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
