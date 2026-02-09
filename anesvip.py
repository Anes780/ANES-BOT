import telebot
import os

# الإعدادات
API_TOKEN = '8570721750:AAHMQZuy28BRhCCtu-4aa5WxLgl_OAqx1qI'
ADMIN_ID = 8353270608
bot = telebot.TeleBot(API_TOKEN)

# --- وظائف الملفات ---
def read_file(file_name, default=""):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            return f.read().strip()
    return default

def write_file(file_name, content):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(str(content))

def append_file(file_name, content):
    if str(content) not in read_file(file_name).splitlines():
        with open(file_name, "a", encoding="utf-8") as f:
            f.write(str(content) + "\n")

# --- لوحة التحكم للمطور ---
def admin_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    count = len(read_file('member.txt').splitlines())
    markup.row(telebot.types.InlineKeyboardButton(f"• المشتركين: {count}", callback_data="m1"))
    markup.row(telebot.types.InlineKeyboardButton("➕ إضافة زر محتوى", callback_data="add_content_btn"), telebot.types.InlineKeyboardButton("🗑 حذف الكل", callback_data="clear_all"))
    markup.row(telebot.types.InlineKeyboardButton("• اذاعهہ‏‏ رسـآله📮", callback_data="send"), telebot.types.InlineKeyboardButton("• وضع اشتراك اجباري💢", callback_data="ach"))
    markup.row(telebot.types.InlineKeyboardButton("• حذف اشتراك🔱", callback_data="dch"))
    return markup

# --- لوحة الأزرار للمستخدمين ---
def user_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = read_file("buttons_map.txt").splitlines()
    for line in buttons:
        if "|" in line:
            btn_id, btn_name = line.split("|")
            markup.add(telebot.types.InlineKeyboardButton(text=btn_name, callback_data=f"user_{btn_id}"))
    return markup

# --- فحص الاشتراك الإجباري ---
def check_sub(user_id):
    channel = read_file("channel.txt")
    if not channel: return True
    try:
        member = bot.get_chat_member(channel, user_id)
        if member.status in ['member', 'administrator', 'creator']: return True
    except: return True
    return False

# --- معالجة الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    if call.data.startswith("user_"):
        btn_id = call.data.replace("user_", "")
        content = read_file(f"content_{btn_id}.txt")
        if content.startswith("file_id:"):
            bot.send_document(chat_id, content.replace("file_id:", ""))
        elif content.startswith("photo_id:"):
            bot.send_photo(chat_id, content.replace("photo_id:", ""))
        else:
            bot.send_message(chat_id, content)
        return

    if call.from_user.id != ADMIN_ID: return
    if call.data == "send":
        bot.edit_message_text("📥 أرسل الإذاعة:", chat_id, call.message.message_id)
        write_file("rembo.txt", "broadcast")
    elif call.data == "ach":
        bot.edit_message_text("💢 أرسل معرف القناة (مثال @MyChannel):", chat_id, call.message.message_id)
        write_file("rembo.txt", "set_channel")
    elif call.data == "dch":
        write_file("channel.txt", "")
        bot.answer_callback_query(call.id, "✅ تم الحذف")
    elif call.data == "add_content_btn":
        bot.edit_message_text("➕ أرسل اسم الزر:", chat_id, call.message.message_id)
        write_file("rembo.txt", "step_name")
    elif call.data == "m1":
        count = len(read_file("member.txt").splitlines())
        bot.answer_callback_query(call.id, f"عدد المشتركين: {count}", show_alert=True)
    elif call.data == "clear_all":
        write_file("buttons_map.txt", "")
        bot.answer_callback_query(call.id, "✅ تم تنظيف الأزرار")

# --- معالجة الرسائل ---
@bot.message_handler(content_types=['text', 'document', 'photo'])
def handle_messages(message):
    user_id = message.from_user.id
    append_file("member.txt", user_id)

    if not check_sub(user_id):
        bot.send_message(message.chat.id, f"⚠️ يجب أن تشترك في القناة أولاً لاستخدام البوت:\n{read_file('channel.txt')}")
        return

    if message.text == "/start":
        bot.send_message(message.chat.id, "مرحباً بك! اختر من القائمة:", reply_markup=user_keyboard())
        return

    if message.text in ["/admin", "/rembo"] and user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "لوحة التحكم:", reply_markup=admin_keyboard())
        return

    if user_id == ADMIN_ID:
        step = read_file("rembo.txt")
        if step == "broadcast":
            for m in read_file("member.txt").splitlines():
                try: bot.send_message(m, message.text)
                except: pass
            bot.send_message(message.chat.id, "✅ تمت الإذاعة.")
            write_file("rembo.txt", "")
        elif step == "set_channel":
            write_file("channel.txt", message.text)
            bot.send_message(message.chat.id, "✅ تم حفظ القناة.")
            write_file("rembo.txt", "")
        elif step == "step_name":
            btn_id = str(message.message_id)
            write_file("temp_btn_id.txt", btn_id)
            write_file("temp_btn_name.txt", message.text)
            bot.send_message(message.chat.id, "✅ أرسل الآن المحتوى (نص، صورة، أو ملف):")
            write_file("rembo.txt", "step_content")
        elif step == "step_content":
            btn_id = read_file("temp_btn_id.txt")
            btn_name = read_file("temp_btn_name.txt")
            if message.content_type == 'text':
                write_file(f"content_{btn_id}.txt", message.text)
            elif message.content_type == 'document':
                write_file(f"content_{btn_id}.txt", f"file_id:{message.document.file_id}")
            elif message.content_type == 'photo':
                write_file(f"content_{btn_id}.txt", f"photo_id:{message.photo[-1].file_id}")
            append_file("buttons_map.txt", f"{btn_id}|{btn_name}")
            bot.send_message(message.chat.id, "✅ تم إنشاء الزر بنجاح!")
            write_file("rembo.txt", "")

bot.polling(none_stop=True)
            
