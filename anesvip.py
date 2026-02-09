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

# --- لوحة التحكم ---
def admin_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton(f"• المشتركين: {len(read_file('member.txt').splitlines())}", callback_data="m1"))
    markup.row(telebot.types.InlineKeyboardButton("➕ إضافة زر", callback_data="add_btn"), telebot.types.InlineKeyboardButton("🗑 حذف زر", callback_data="del_btn"))
    markup.row(telebot.types.InlineKeyboardButton("• اذاعهہ‏‏ رسـآله📮", callback_data="send"), telebot.types.InlineKeyboardButton("• توجہيه رسالهہ‏‏‏‏🔄", callback_data="forward"))
    markup.row(telebot.types.InlineKeyboardButton("• وضع اشتراك اجباري💢", callback_data="ach"), telebot.types.InlineKeyboardButton("• حذف اشتراك اجباري🔱", callback_data="dch"))
    markup.row(telebot.types.InlineKeyboardButton("• تفعيل التنبيه✔️", callback_data="ons"), telebot.types.InlineKeyboardButton("• تعطيل التنبيه❎", callback_data="ofs"))
    markup.row(telebot.types.InlineKeyboardButton("فتح البوت✅", callback_data="obot"), telebot.types.InlineKeyboardButton("ايقاف البوت❌", callback_data="ofbot"))
    markup.row(telebot.types.InlineKeyboardButton("حظر عضو✅", callback_data="ban"), telebot.types.InlineKeyboardButton("الغاء حظر عضو❌", callback_data="unban"))
    return markup

# --- معالجة الأزرار (هنا تم تفعيل الاشتراك والإذاعة) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    if call.from_user.id != ADMIN_ID: return

    if call.data == "send":
        bot.edit_message_text("📥 أرسل الآن الرسالة التي تريد إذاعتها للمشتركين:", chat_id, call.message.message_id)
        write_file("rembo.txt", "broadcast")

    elif call.data == "forward":
        bot.edit_message_text("🔄 قم بتوجيه (Forward) الرسالة التي تريد نشرها هنا:", chat_id, call.message.message_id)
        write_file("rembo.txt", "fwd_broadcast")

    elif call.data == "ach":
        bot.edit_message_text("💢 أرسل الآن معرف القناة للاشتراك الإجباري (مثال: @MyChannel):", chat_id, call.message.message_id)
        write_file("rembo.txt", "set_channel")

    elif call.data == "dch":
        write_file("channel.txt", "")
        bot.answer_callback_query(call.id, "✅ تم حذف الاشتراك الإجباري", show_alert=True)

    # بقية أزرار الإضافة والحذف
    elif call.data == "add_btn":
        bot.edit_message_text("➕ أرسل اسم الزر الجديد:", chat_id, call.message.message_id)
        write_file("rembo.txt", "add_name")
    
    elif call.data == "m1":
        count = len(read_file("member.txt").splitlines())
        bot.answer_callback_query(call.id, f"عدد المشتركين: {count}", show_alert=True)

# --- معالجة الرسائل ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    # حفظ المشتركين
    append_file("member.txt", user_id)

    if text in ["/admin", "/rembo"] and user_id == ADMIN_ID:
        bot.send_message(chat_id, "اهلا بڪ عزيزي المطور، اليڪ اوامرڪ⚡📮", reply_markup=admin_keyboard())
        return

    # تنفيذ أوامر الأدمن بناءً على الحالة (Step)
    if user_id == ADMIN_ID:
        step = read_file("rembo.txt")

        if step == "broadcast": # الإذاعة
            members = read_file("member.txt").splitlines()
            count = 0
            for m in members:
                try:
                    bot.send_message(m, text)
                    count += 1
                except: pass
            bot.send_message(chat_id, f"✅ تمت الإذاعة لـ {count} مشترك.", reply_markup=admin_keyboard())
            write_file("rembo.txt", "")

        elif step == "set_channel": # تعيين القناة
            write_file("channel.txt", text)
            bot.send_message(chat_id, f"✅ تم حفظ القناة: {text}", reply_markup=admin_keyboard())
            write_file("rembo.txt", "")

        elif step == "add_name":
            write_file("temp_name.txt", text)
            bot.send_message(chat_id, "🔗 أرسل الرابط الآن:")
            write_file("rembo.txt", "add_url")
            
        elif step == "add_url":
            name = read_file("temp_name.txt")
            append_file("custom_buttons.txt", f"{name}|{text}")
            bot.send_message(chat_id, "✅ تم إضافة الزر.", reply_markup=admin_keyboard())
            write_file("rembo.txt", "")

bot.polling(none_stop=True)
