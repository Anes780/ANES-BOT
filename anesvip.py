import telebot
import os

# الإعدادات
API_TOKEN = '8570721750:AAHMQZuy28BRhCCtu-4aa5WxLgl_OAqx1qI'
ADMIN_ID = 8353270608
bot = telebot.TeleBot(API_TOKEN)

# وظائف الملفات
def read_file(file_name, default=""):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            return f.read().strip()
    return default

def write_file(file_name, content):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(str(content))

# لوحة التحكم للمطور
def admin_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("➕ إضافة زر محتوى", callback_data="add_content_btn"))
    markup.row(telebot.types.InlineKeyboardButton("🗑 حذف الكل", callback_data="clear_all"))
    return markup

# لوحة الأزرار للمستخدمين
def user_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = read_file("buttons_map.txt").splitlines()
    for line in buttons:
        if "|" in line:
            btn_id, btn_name = line.split("|")
            markup.add(telebot.types.InlineKeyboardButton(text=btn_name, callback_data=f"user_{btn_id}"))
    return markup

# معالجة الضغط على الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    
    # إذا ضغط المستخدم العادي على زر محتوى
    if call.data.startswith("user_"):
        btn_id = call.data.replace("user_", "")
        content = read_file(f"content_{btn_id}.txt")
        if content.startswith("file_id:"):
            bot.send_document(chat_id, content.replace("file_id:", ""))
        else:
            bot.send_message(chat_id, content)
            
    # أوامر الأدمن
    if call.from_user.id == ADMIN_ID:
        if call.data == "add_content_btn":
            bot.edit_message_text("➕ أرسل اسم الزر الجديد:", chat_id, call.message.message_id)
            write_file("rembo.txt", "step_name")
        elif call.data == "clear_all":
            write_file("buttons_map.txt", "")
            bot.answer_callback_query(call.id, "✅ تم حذف جميع الأزرار")

# معالجة الرسائل
@bot.message_handler(content_types=['text', 'document', 'photo'])
def handle_messages(message):
    user_id = message.from_user.id
    
    if message.text == "/start":
        bot.send_message(message.chat.id, "مرحباً بك! اختر المحتوى:", reply_markup=user_keyboard())
        return

    if message.text == "/admin" and user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "لوحة التحكم:", reply_markup=admin_keyboard())
        return

    # خطوات إضافة الزر (للأدمن فقط)
    if user_id == ADMIN_ID:
        step = read_file("rembo.txt")
        
        if step == "step_name":
            btn_id = str(message.message_id)
            write_file("temp_btn_id.txt", btn_id)
            write_file("temp_btn_name.txt", message.text)
            bot.send_message(message.chat.id, f"✅ تم حفظ الاسم: {message.text}\nالآن أرسل المحتوى (نص أو ملف):")
            write_file("rembo.txt", "step_content")
            
        elif step == "step_content":
            btn_id = read_file("temp_btn_id.txt")
            btn_name = read_file("temp_btn_name.txt")
            
            if message.content_type == 'text':
                write_file(f"content_{btn_id}.txt", message.text)
            elif message.content_type == 'document':
                write_file(f"content_{btn_id}.txt", f"file_id:{message.document.file_id}")
            
            with open("buttons_map.txt", "a") as f:
                f.write(f"{btn_id}|{btn_name}\n")
                
            bot.send_message(message.chat.id, "✅ تم إنشاء الزر بنجاح!", reply_markup=admin_keyboard())
            write_file("rembo.txt", "")

bot.polling(none_stop=True)
    
