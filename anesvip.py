import telebot
import json
import os
import time
import csv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


TOKEN = '8570721750:AAHMQZuy28BRhCCtu-4aa5WxLgl_OAqx1qI'
DATA_FILE = 'data5.json'
bot = telebot.TeleBot(TOKEN)


FIXED_OWNER_ID = '8353270608'  

DEFAULT_DATA = {
    'owner': FIXED_OWNER_ID,  
    'admins': [],
    'channels': [],
    'users': [],
    'sections': {}  
}


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}
    
    for key, default in DEFAULT_DATA.items():
        if key not in data:
            data[key] = default.copy() if isinstance(default, (list, dict)) else default
    
    
    data['owner'] = FIXED_OWNER_ID
    
    
    owner_exists = False
    for admin in data['admins']:
        if admin['id'] == FIXED_OWNER_ID:
            owner_exists = True
            break
    
    if not owner_exists:
        data['admins'].insert(0, {
            'id': FIXED_OWNER_ID,
            'first_name': 'ANES',
            'username': '@anes443'
        })
    
    return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def is_owner(user_id):
    return str(user_id) == FIXED_OWNER_ID

def is_admin(user_id):
    data = load_data()
    return is_owner(user_id) or str(user_id) in [admin['id'] for admin in data['admins']]


def check_subscription(user_id):
    data = load_data()
    for channel in data['channels']:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True


def sanitize_text(text):
    
    if text is None:
        return "بدون اسم"
    
    
    problematic_chars = ['<', '>', '&', '"', "'", '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!']
    
    
    sanitized = str(text)
    for char in problematic_chars:
        sanitized = sanitized.replace(char, ' ')
    
    
    sanitized = ' '.join(sanitized.split())
    
    return sanitized if sanitized.strip() else "بدون اسم"


def admin_panel_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('📢 إرسال إعلان', callback_data='broadcast'),
        InlineKeyboardButton('➕ إضافة قناة', callback_data='add_channel'),
        InlineKeyboardButton('🗑️ حذف قناة', callback_data='remove_channel'),
        InlineKeyboardButton('👑 إضافة مشرف', callback_data='add_admin'),
        InlineKeyboardButton('👥 عرض المشرفين والقنوات', callback_data='view_admins_channels'),
        InlineKeyboardButton('📂 إدارة الأقسام', callback_data='manage_sections'),
        InlineKeyboardButton('🗂️ إدارة المحتوى', callback_data='manage_content')
    )
    return kb

def user_panel_keyboard():
    data = load_data()
    kb = InlineKeyboardMarkup(row_width=2)
    
    
    if data['sections']:
        for section_name in data['sections']:
            kb.add(InlineKeyboardButton(section_name, callback_data=f'view_section|{section_name}'))
    
    
    kb.add(
        InlineKeyboardButton('📢 القنوات', callback_data='view_channels'),
        InlineKeyboardButton('🔄 تحديث الاشتراك', callback_data='check_subscription')
    )
    return kb

def sections_management_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    
    
    kb.add(
        InlineKeyboardButton('➕ إنشاء قسم جديد', callback_data='add_section'),
        InlineKeyboardButton('🗑️ حذف قسم', callback_data='delete_section'),
        InlineKeyboardButton('⬅️ رجوع', callback_data='back|admin')
    )
    
    
    kb.add(InlineKeyboardButton('📋 قائمة الأقسام', callback_data='list_sections'))
    
    return kb

def content_management_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    
    kb.add(
        InlineKeyboardButton('➕ إضافة محتوى', callback_data='add_content'),
        InlineKeyboardButton('🗑️ حذف محتوى', callback_data='delete_content'),
        InlineKeyboardButton('📁 عرض المحتوى', callback_data='view_content'),
        InlineKeyboardButton('📊 تصدير ملف data5.json', callback_data='export_data_file'),
        InlineKeyboardButton('⬅️ رجوع', callback_data='back|admin')
    )
    return kb

def admin_content_keyboard(section_name):
    data = load_data()
    kb = InlineKeyboardMarkup()
    
    if section_name in data['sections'] and data['sections'][section_name]:
        for idx, content_data in enumerate(data['sections'][section_name]):
            content_name = content_data.get('name', f'محتوى {idx+1}')
            kb.row(
                InlineKeyboardButton(content_name, callback_data=f'view_item|{section_name}|{idx}'),
                InlineKeyboardButton('🗑️', callback_data=f'remove_content|{section_name}|{idx}')
            )
    
    kb.add(InlineKeyboardButton('➕ إضافة محتوى', callback_data=f'add_to_section|{section_name}'))
    kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|content'))
    return kb

def sections_list_keyboard(action=None):
    data = load_data()
    kb = InlineKeyboardMarkup(row_width=1)
    
    for section_name in data['sections']:
        kb.add(InlineKeyboardButton(section_name, callback_data=f'select_section|{section_name}|{action}'))
    
    if action:
        kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|content'))
    else:
        kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|sections'))
    return kb

def back_keyboard(back_to):
    """لوحة مفاتيح زر الرجوع"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data=f'back|{back_to}'))
    return kb


@bot.message_handler(commands=['start'])
def handle_start(msg):
    data = load_data()
    uid = str(msg.from_user.id)
    
    
    user_first_name = sanitize_text(msg.from_user.first_name)
    user_username = sanitize_text(f"@{msg.from_user.username}" if msg.from_user.username else "بدون معرف")
    
    
    user_found = False
    for user in data['users']:
        if user['id'] == uid:
            user['first_name'] = user_first_name
            user['username'] = user_username
            user_found = True
            break
    
    if not user_found:
        data['users'].append({
            'id': uid,
            'first_name': user_first_name,
            'username': user_username,
            'joined_date': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        save_data(data)
    
    
    if uid == FIXED_OWNER_ID:
        owner_message = f"""
<b>👑 مرحباً بك أيها المالك</b>

<b>🆔 معرفك:</b> <code>{uid}</code>
<b>👤 اسم المستخدم:</b> {user_username}

<b>🎯 أنت المالك الثابت للبوت ولديك جميع الصلاحيات.</b>
<b>👁️‍🗨️ يمكنك إدارة البوت من خلال اللوحة أدناه:</b>
"""
        if data['channels'] and not check_subscription(msg.from_user.id):
            show_channels(msg.chat.id, "📢 يجب الاشتراك في القنوات التالية أولاً:")
            return
        
        show_main_menu(msg.chat.id, True, owner_message)
        return
    
    # إنشاء رسالة الترحيب العادية للمستخدمين
    welcome_message = f"""
<b>👋ANES VIP أهلاً وسهلاً بك في بوت {user_first_name}</b>

<b>🆔 معرفك:</b> <code>{uid}</code>
<b>👤 اسم المستخدم:</b> {user_username}

<b>🦋ANES VIP مرحباً بك في بوت</b>
<b>اختر أحد الخيارات المتاحة ☃️</b>
"""
    
    if data['channels'] and not check_subscription(msg.from_user.id):
        show_channels(msg.chat.id, "📢 يجب الاشتراك في القنوات التالية أولاً:")
        return
    
    show_main_menu(msg.chat.id, is_admin(msg.from_user.id), welcome_message)

def show_main_menu(chat_id, is_admin_user, welcome_message=None):
    if welcome_message is None:
        
        welcome_message = "<b>👤ANES VIP مرحباً بك في بوت</b>\n\n<b>اختر أحد الخيارات المتاحة ☃️</b>"
    
    if is_admin_user:
        bot.send_message(chat_id, welcome_message, parse_mode='HTML', reply_markup=admin_panel_keyboard())
    else:
        bot.send_message(chat_id, welcome_message, parse_mode='HTML', reply_markup=user_panel_keyboard())

def show_channels(chat_id, message="📢 القنوات المطلوبة:"):
    data = load_data()
    if data['channels']:
        txt = "\n".join([f"🔹 {ch}" for ch in data['channels']])
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('🔄 تأكيد الاشتراك', callback_data='check_subscription'))
        bot.send_message(chat_id, f"<b>{message}</b>\n{txt}", parse_mode='HTML', reply_markup=kb)
    else:
        bot.send_message(chat_id, '<b>📭 لا توجد قنوات حالياً</b>', parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(c):
    data = load_data()
    uid = str(c.from_user.id)
    
    
    if data['channels'] and not check_subscription(c.from_user.id) and not c.data.startswith('check_subscription'):
        bot.answer_callback_query(c.id, "⚠️ يجب الاشتراك في القنوات أولاً", show_alert=True)
        show_channels(c.message.chat.id, "📢 يجب الاشتراك في القنوات التالية أولاً:")
        return
    
    
    if is_admin(c.from_user.id):
        handle_admin_callbacks(c)
    
    else:
        handle_user_callbacks(c)
    
    bot.answer_callback_query(c.id)

def handle_admin_callbacks(c):
    data = load_data()
    
    if c.data == 'broadcast':
        msg = bot.send_message(c.message.chat.id, '<b>📢 أرسل الإعلان:</b>', parse_mode='HTML', reply_markup=back_keyboard('admin'))
        
        bot.register_next_step_handler(msg, do_broadcast, msg.message_id)
    
    elif c.data == 'add_channel':
        msg = bot.send_message(c.message.chat.id, '<b>➕ أرسل معرف القناة (@...):</b>', parse_mode='HTML', reply_markup=back_keyboard('admin'))
        bot.register_next_step_handler(msg, do_add_channel, msg.message_id)
    
    elif c.data == 'remove_channel':
        if not data['channels']:
            bot.answer_callback_query(c.id, '⚠️ لا توجد قنوات', show_alert=True)
            return
        
        kb = InlineKeyboardMarkup()
        for ch in data['channels']:
            kb.add(InlineKeyboardButton(ch, callback_data=f'rmch|{ch}'))
        kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|admin'))
        bot.edit_message_text('<b>🗑️ اختر قناة للحذف:</b>', 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=kb)
    
    elif c.data.startswith('rmch|'):
        ch = c.data.split('|',1)[1]
        if ch in data['channels']:
            data['channels'].remove(ch)
            save_data(data)
            bot.answer_callback_query(c.id, f'✅ حُذفت {ch}')
            
            c.data = 'remove_channel'
            handle_admin_callbacks(c)
        else:
            bot.answer_callback_query(c.id, '⚠️ القناة غير موجودة', show_alert=True)
    
    elif c.data == 'add_admin':
        if is_owner(c.from_user.id):
            msg = bot.send_message(c.message.chat.id, '<b>➕ أرسل آيدي المشرف الجديد:</b>', parse_mode='HTML', reply_markup=back_keyboard('admin'))
            bot.register_next_step_handler(msg, do_add_admin, msg.message_id)
        else:
            bot.answer_callback_query(c.id, '⚠️ فقط المالك يستطيع', show_alert=True)
    
    elif c.data == 'view_admins_channels':
        msg_text = "<b>👑 المالك:</b>\n"
        try:
            owner_info = next((admin for admin in data['admins'] if admin['id'] == data['owner']), None)
            if owner_info:
                msg_text += f"└ {owner_info['first_name']} ({owner_info['username']}) - ID: <code>{data['owner']}</code>\n\n"
            else:
                msg_text += f"└ ID: <code>{data['owner']}</code>\n\n"
        except:
            msg_text += f"└ ID: <code>{data['owner']}</code>\n\n"
        
        msg_text += "<b>👥 المشرفين:</b>\n"
        for admin in data['admins']:
            if admin['id'] == data['owner']:
                continue
            msg_text += f"└ {admin['first_name']} ({admin['username']}) - ID: <code>{admin['id']}</code>\n"
        
        msg_text += "\n<b>📢 القنوات:</b>\n"
        for channel in data['channels']:
            msg_text += f"└ {channel}\n"
        
        
        msg_text += f"\n<b>👥 عدد المستخدمين:</b> {len(data['users'])}"
        
        kb = InlineKeyboardMarkup()
        if is_owner(c.from_user.id):
            for admin in data['admins']:
                if admin['id'] != data['owner']:
                    label = f"حذف مشرف {admin['first_name'][:10]}" if admin['first_name'] else f"حذف مشرف {admin['id'][:6]}"
                    kb.add(InlineKeyboardButton(label, callback_data=f'rmadm|{admin["id"]}'))
        kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|admin'))
        
        bot.edit_message_text(msg_text, c.message.chat.id, c.message.message_id, 
                             parse_mode='HTML', reply_markup=kb)
    
    elif c.data.startswith('rmadm|'):
        if is_owner(c.from_user.id):
            admin_id = c.data.split('|')[1]
            if admin_id != str(data['owner']):
                found = False
                for admin in data['admins']:
                    if admin['id'] == admin_id:
                        data['admins'].remove(admin)
                        save_data(data)
                        bot.answer_callback_query(c.id, f'✅ تم حذف المشرف {admin_id}')
                        found = True
                        break
                
                if found:
                    
                    c.data = 'view_admins_channels'
                    handle_admin_callbacks(c)
                else:
                    bot.answer_callback_query(c.id, '⚠️ المشرف غير موجود', show_alert=True)
            else:
                bot.answer_callback_query(c.id, '⚠️ لا يمكن حذف المالك', show_alert=True)
        else:
            bot.answer_callback_query(c.id, '⚠️ فقط المالك يستطيع', show_alert=True)
    
    elif c.data == 'manage_sections':
        bot.edit_message_text('<b>📂 إدارة الأقسام</b>\n\nاختر أحد الخيارات:', 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=sections_management_keyboard())
    
    elif c.data == 'manage_content':
        bot.edit_message_text('<b>🗂️ إدارة المحتوى</b>\n\nاختر أحد الخيارات:', 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=content_management_keyboard())
    
    elif c.data == 'add_section':
        msg = bot.send_message(c.message.chat.id, '<b>➕ أرسل اسم القسم الجديد:</b>', parse_mode='HTML', reply_markup=back_keyboard('sections'))
        bot.register_next_step_handler(msg, process_add_section, msg.message_id)
    
    elif c.data == 'delete_section':
        if not data['sections']:
            bot.answer_callback_query(c.id, '⚠️ لا توجد أقسام لحذفها', show_alert=True)
            return
        
        kb = InlineKeyboardMarkup(row_width=1)
        for section_name in data['sections']:
            kb.add(InlineKeyboardButton(section_name, callback_data=f'delete_section_now|{section_name}'))
        
        kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|sections'))
        
        bot.edit_message_text('<b>🗑️ اختر قسم لحذفه:</b>', 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=kb)
    
    elif c.data.startswith('delete_section_now|'):
        section_name = c.data.split('|')[1]
        data = load_data()
        
        if section_name in data['sections']:
            del data['sections'][section_name]
            save_data(data)
            bot.answer_callback_query(c.id, f'✅ تم حذف قسم: {section_name}')
            bot.edit_message_text(f'<b>✅ تم حذف قسم: {section_name}</b>', 
                                  c.message.chat.id, c.message.message_id,
                                  parse_mode='HTML', reply_markup=sections_management_keyboard())
        else:
            bot.answer_callback_query(c.id, '⚠️ القسم غير موجود', show_alert=True)
    
    elif c.data == 'list_sections':
        if not data['sections']:
            bot.answer_callback_query(c.id, '⚠️ لا توجد أقسام', show_alert=True)
            return
        
        sections_text = "<b>📋 قائمة الأقسام:</b>\n\n"
        for idx, section_name in enumerate(data['sections'], 1):
            content_count = len(data['sections'][section_name])
            sections_text += f"{idx}. {section_name} ({content_count} محتوى)\n"
        
        bot.edit_message_text(sections_text, 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=sections_management_keyboard())
    
    elif c.data.startswith('select_section|'):
        parts = c.data.split('|')
        section_name = parts[1]
        action = parts[2] if len(parts) > 2 else None
        
        if action == 'add_content':
            
            msg = bot.send_message(c.message.chat.id, '<b>📤 أرسل أي نوع من المحتوى (نص، صورة، فيديو، ملف، إيموجي، إلخ):</b>', parse_mode='HTML', reply_markup=back_keyboard('content'))
            bot.register_next_step_handler(msg, lambda m: process_add_content(m, section_name, msg.message_id))
        
        elif action == 'delete_content':
            
            bot.edit_message_text(f'<b>🗑️ محتوى قسم: {section_name}</b>', 
                                  c.message.chat.id, c.message.message_id,
                                  parse_mode='HTML', reply_markup=admin_content_keyboard(section_name))
        
        elif action == 'view_content':
            
            bot.edit_message_text(f'<b>📂 محتوى قسم: {section_name}</b>', 
                                  c.message.chat.id, c.message.message_id,
                                  parse_mode='HTML', reply_markup=admin_content_keyboard(section_name))
    
    elif c.data.startswith('add_to_section|'):
        section_name = c.data.split('|')[1]
        msg = bot.send_message(c.message.chat.id, '<b>📤 أرسل أي نوع من المحتوى (نص، صورة، فيديو، ملف، إيموجي، إلخ):</b>', parse_mode='HTML', reply_markup=back_keyboard('content'))
        bot.register_next_step_handler(msg, lambda m: process_add_content(m, section_name, msg.message_id))
    
    elif c.data == 'add_content':
        if not data['sections']:
            bot.answer_callback_query(c.id, '⚠️ يجب إنشاء أقسام أولاً', show_alert=True)
            return
        
        kb = InlineKeyboardMarkup(row_width=1)
        for section_name in data['sections']:
            kb.add(InlineKeyboardButton(section_name, callback_data=f'select_section|{section_name}|add_content'))
        
        kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|content'))
        
        bot.edit_message_text('<b>📁 اختر قسم لإضافة محتوى له:</b>', 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=kb)
    
    elif c.data == 'delete_content':
        if not data['sections']:
            bot.answer_callback_query(c.id, '⚠️ لا توجد أقسام', show_alert=True)
            return
        
        kb = InlineKeyboardMarkup(row_width=1)
        for section_name in data['sections']:
            kb.add(InlineKeyboardButton(section_name, callback_data=f'select_section|{section_name}|delete_content'))
        
        kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|content'))
        
        bot.edit_message_text('<b>🗑️ اختر قسم لحذف محتوى منه:</b>', 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=kb)
    
    elif c.data == 'view_content':
        if not data['sections']:
            bot.answer_callback_query(c.id, '⚠️ لا توجد أقسام', show_alert=True)
            return
        
        kb = InlineKeyboardMarkup(row_width=1)
        for section_name in data['sections']:
            kb.add(InlineKeyboardButton(section_name, callback_data=f'select_section|{section_name}|view_content'))
        
        kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|content'))
        
        bot.edit_message_text('<b>📁 اختر قسم لعرض محتواه:</b>', 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=kb)
    
    elif c.data.startswith('remove_content|'):
        parts = c.data.split('|')
        section_name = parts[1]
        content_idx = int(parts[2])
        
        if section_name in data['sections'] and len(data['sections'][section_name]) > content_idx:
            
            content_name = data['sections'][section_name][content_idx].get('name', 'محتوى بدون اسم')
            del data['sections'][section_name][content_idx]
            save_data(data)
            
            
            if data['sections'][section_name]:
                bot.edit_message_text(f'<b>🗑️ تم حذف: {content_name}</b>\n\n<b>📂 محتوى قسم: {section_name}</b>', 
                                      c.message.chat.id, c.message.message_id,
                                      parse_mode='HTML', reply_markup=admin_content_keyboard(section_name))
            else:
                bot.edit_message_text(f'<b>✅ تم حذف آخر محتوى من القسم: {section_name}</b>', 
                                      c.message.chat.id, c.message.message_id,
                                      parse_mode='HTML', reply_markup=content_management_keyboard())
        else:
            bot.answer_callback_query(c.id, '⚠️ المحتوى غير موجود', show_alert=True)
    
    elif c.data.startswith('view_item|'):
        parts = c.data.split('|')
        section_name = parts[1]
        content_idx = int(parts[2])
        
        if section_name in data['sections'] and len(data['sections'][section_name]) > content_idx:
            content_data = data['sections'][section_name][content_idx]
            content_type = content_data['type']
            content_value = content_data['content']
            
            
            try:
                if content_type == 'text':
                    bot.send_message(c.message.chat.id, content_value, parse_mode='HTML')
                elif content_type == 'photo':
                    bot.send_photo(c.message.chat.id, content_value)
                elif content_type == 'video':
                    bot.send_video(c.message.chat.id, content_value)
                elif content_type == 'document':
                    bot.send_document(c.message.chat.id, content_value)
                elif content_type == 'audio':
                    bot.send_audio(c.message.chat.id, content_value)
                elif content_type == 'voice':
                    bot.send_voice(c.message.chat.id, content_value)
                elif content_type == 'sticker':
                    bot.send_sticker(c.message.chat.id, content_value)
                elif content_type == 'animation':
                    bot.send_animation(c.message.chat.id, content_value)
            except Exception as e:
                bot.send_message(c.message.chat.id, f'<b>❌ فشل في إرسال المحتوى:</b>\n{str(e)}', parse_mode='HTML')
        else:
            bot.answer_callback_query(c.id, '⚠️ المحتوى غير موجود', show_alert=True)
    
    elif c.data == 'export_data_file':
        if is_owner(c.from_user.id):
            export_data_file(c.message.chat.id)
        else:
            bot.answer_callback_query(c.id, '⚠️ فقط المالك يستطيع', show_alert=True)
    
    elif any(c.data.startswith(pref) for pref in ['back|']):
        handle_back_commands(c)

def handle_user_callbacks(c):
    data = load_data()
    
    if c.data == 'view_channels':
        show_channels(c.message.chat.id)
    
    elif c.data == 'check_subscription':
        if check_subscription(c.from_user.id):
            bot.answer_callback_query(c.id, '✅ أنت مشترك في جميع القنوات', show_alert=True)
            recreate_welcome_message(c, False)
        else:
            bot.answer_callback_query(c.id, '❌ يجب الاشتراك في جميع القنوات', show_alert=True)
            show_channels(c.message.chat.id, "📢 يجب الاشتراك في القنوات التالية أولاً:")
    
    elif c.data.startswith('view_section|'):
        section_name = c.data.split('|')[1]
        show_section_content(c, section_name)
    
    elif c.data.startswith('content|'):
        parts = c.data.split('|')
        section_name = parts[1]
        content_idx = int(parts[2])
        
        if section_name in data['sections'] and len(data['sections'][section_name]) > content_idx:
            content_data = data['sections'][section_name][content_idx]
            content_type = content_data['type']
            content_value = content_data['content']
            
            
            try:
                if content_type == 'text':
                    bot.send_message(c.message.chat.id, content_value, parse_mode='HTML')
                elif content_type == 'photo':
                    bot.send_photo(c.message.chat.id, content_value)
                elif content_type == 'video':
                    bot.send_video(c.message.chat.id, content_value)
                elif content_type == 'document':
                    bot.send_document(c.message.chat.id, content_value)
                elif content_type == 'audio':
                    bot.send_audio(c.message.chat.id, content_value)
                elif content_type == 'voice':
                    bot.send_voice(c.message.chat.id, content_value)
                elif content_type == 'sticker':
                    bot.send_sticker(c.message.chat.id, content_value)
                elif content_type == 'animation':
                    bot.send_animation(c.message.chat.id, content_value)
            except Exception as e:
                bot.answer_callback_query(c.id, f'❌ فشل في إرسال المحتوى: {str(e)}', show_alert=True)
        else:
            bot.answer_callback_query(c.id, '⚠️ المحتوى غير موجود', show_alert=True)
    
    elif c.data == 'back|user':
        recreate_welcome_message(c, False)

def recreate_welcome_message(c, is_admin_user):
    
    user_first_name = sanitize_text(c.from_user.first_name)
    user_username = sanitize_text(f"@{c.from_user.username}" if c.from_user.username else "بدون معرف")
    uid = str(c.from_user.id)
    
    welcome_message = f"""
<b>👋 أهلاً وسهلاً بك {user_first_name}</b>

<b>🆔 معرفك:</b> <code>{uid}</code>
<b>👤 اسم المستخدم:</b> {user_username}

<b>🦋 مرحباً بك في بوت ANES VIP</b>
<b>اختر أحد الخيارات المتاحة ☃️</b>
"""
    
    if is_admin_user:
        bot.edit_message_text(welcome_message, c.message.chat.id, c.message.message_id,
                             parse_mode='HTML', reply_markup=admin_panel_keyboard())
    else:
        bot.edit_message_text(welcome_message, c.message.chat.id, c.message.message_id,
                             parse_mode='HTML', reply_markup=user_panel_keyboard())

def show_section_content(c, section_name):
    data = load_data()
    if section_name in data['sections'] and data['sections'][section_name]:
        
        kb = InlineKeyboardMarkup(row_width=1)
        for idx, content_data in enumerate(data['sections'][section_name]):
            content_name = content_data.get('name', f'محتوى {idx+1}')
            kb.add(InlineKeyboardButton(content_name, callback_data=f'content|{section_name}|{idx}'))
        
        kb.add(InlineKeyboardButton('⬅️ رجوع', callback_data='back|user'))
        
        bot.edit_message_text(
            f'<b>📂 {section_name}</b>\n\nاختر المحتوى الذي تريد مشاهدته',
            c.message.chat.id,
            c.message.message_id,
            parse_mode='HTML',
            reply_markup=kb
        )
    else:
        bot.answer_callback_query(c.id, '⚠️ لا توجد محتويات في هذا القسم حالياً', show_alert=True)

def handle_back_commands(c):
    parts = c.data.split('|')
    back_to = parts[1]
    
    if back_to == 'admin':
        recreate_welcome_message(c, True)
    
    elif back_to == 'sections':
        bot.edit_message_text('<b>📂 إدارة الأقسام</b>\n\nاختر أحد الخيارات:', 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=sections_management_keyboard())
    
    elif back_to == 'content':
        bot.edit_message_text('<b>🗂️ إدارة المحتوى</b>\n\nاختر أحد الخيارات:', 
                              c.message.chat.id, c.message.message_id,
                              parse_mode='HTML', reply_markup=content_management_keyboard())
    
    elif back_to == 'user':
        recreate_welcome_message(c, False)


def export_data_file(chat_id):
    """تصدير ملف data5.json للمالك"""
    try:
        if os.path.exists(DATA_FILE):
            
            data = load_data()
            
            
            with open(DATA_FILE, 'rb') as file:
                caption = f"""<b>📁 ملف البيانات المصدّر</b>

<b>📊 إحصائيات البيانات:</b>
👑 المالك: {data['owner']}
👥 عدد المشرفين: {len(data['admins'])}
📢 عدد القنوات: {len(data['channels'])}
👤 عدد المستخدمين: {len(data['users'])}
📂 عدد الأقسام: {len(data['sections'])}

📅 وقت التصدير: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
                bot.send_document(chat_id, file, caption=caption, parse_mode='HTML')
        else:
            bot.send_message(chat_id, '<b>⚠️ ملف البيانات غير موجود</b>', parse_mode='HTML')
    except Exception as e:
        bot.send_message(chat_id, f'<b>❌ خطأ في تصدير الملف:</b>\n{str(e)}', parse_mode='HTML')


def process_add_section(message, msg_id):
    
    if hasattr(message, 'data') and message.data.startswith('back|'):
        
        try:
            bot.delete_message(message.chat.id, msg_id)
        except:
            pass
        return
    
    section_name = message.text.strip()
    data = load_data()
    
    if not section_name:
        bot.send_message(message.chat.id, '<b>⚠️ يجب إدخال اسم صحيح</b>', parse_mode='HTML')
        return
    
    if section_name in data['sections']:
        bot.send_message(message.chat.id, '<b>⚠️ هذا القسم موجود مسبقاً</b>', parse_mode='HTML')
        return
    
    
    data['sections'][section_name] = []
    save_data(data)
    
    
    try:
        bot.delete_message(message.chat.id, msg_id)
    except:
        pass
    
    bot.send_message(message.chat.id, f'<b>✅ تم إنشاء قسم جديد: {section_name}</b>', parse_mode='HTML')
    bot.send_message(message.chat.id, '<b>📂 إدارة الأقسام</b>\n\nاختر أحد الخيارات:', 
                     parse_mode='HTML', reply_markup=sections_management_keyboard())


def process_add_content(message, section_name, msg_id):
    
    if hasattr(message, 'data') and message.data.startswith('back|'):
        
        try:
            bot.delete_message(message.chat.id, msg_id)
        except:
            pass
        return
    
    data = load_data()
    
    if section_name not in data['sections']:
        bot.send_message(message.chat.id, '<b>⚠️ القسم غير موجود</b>', parse_mode='HTML')
        return
    
    content_data = {'type': '', 'content': '', 'name': ''}
    
    
    if message.text:
        content_data['type'] = 'text'
        content_data['content'] = message.text
        content_data['name'] = sanitize_text(message.text[:30] + "..." if len(message.text) > 30 else message.text)
    elif message.photo:
        content_data['type'] = 'photo'
        content_data['content'] = message.photo[-1].file_id
        content_data['name'] = "صورة"
    elif message.video:
        content_data['type'] = 'video'
        content_data['content'] = message.video.file_id
        content_data['name'] = "فيديو"
    elif message.document:
        content_data['type'] = 'document'
        content_data['content'] = message.document.file_id
        content_data['name'] = sanitize_text(message.document.file_name if message.document.file_name else "ملف")
    elif message.audio:
        content_data['type'] = 'audio'
        content_data['content'] = message.audio.file_id
        content_data['name'] = sanitize_text(message.audio.title if message.audio.title else "صوت")
    elif message.voice:
        content_data['type'] = 'voice'
        content_data['content'] = message.voice.file_id
        content_data['name'] = "رسالة صوتية"
    elif message.sticker:
        content_data['type'] = 'sticker'
        content_data['content'] = message.sticker.file_id
        content_data['name'] = "ملصق"
    elif message.animation:
        content_data['type'] = 'animation'
        content_data['content'] = message.animation.file_id
        content_data['name'] = "صورة متحركة"
    else:
        bot.send_message(message.chat.id, '<b>⚠️ نوع المحتوى غير مدعوم</b>', parse_mode='HTML')
        return
    
    
    data['sections'][section_name].append(content_data)
    save_data(data)
    
    
    try:
        bot.delete_message(message.chat.id, msg_id)
    except:
        pass
    
    bot.send_message(message.chat.id, f'<b>✅ تم إضافة محتوى إلى قسم {section_name}</b>', parse_mode='HTML')
    bot.send_message(message.chat.id, '<b>🗂️ إدارة المحتوى</b>\n\nاختر أحد الخيارات:', 
                     parse_mode='HTML', reply_markup=content_management_keyboard())


def do_broadcast(message, msg_id):
    
    if hasattr(message, 'data') and message.data.startswith('back|'):
        
        try:
            bot.delete_message(message.chat.id, msg_id)
        except:
            pass
        return
    
    data = load_data()
    total = len(data['users'])
    sent = 0
    for user in data['users']:
        try:
            bot.copy_message(user['id'], message.chat.id, message.message_id)
            sent += 1
            time.sleep(0.1)
        except:
            continue
    
    
    try:
        bot.delete_message(message.chat.id, msg_id)
    except:
        pass
    
    bot.send_message(message.chat.id, f'<b>✅ تم الإرسال:</b> {sent}/{total}', parse_mode='HTML')

def do_add_channel(message, msg_id):
    
    if hasattr(message, 'data') and message.data.startswith('back|'):
        
        try:
            bot.delete_message(message.chat.id, msg_id)
        except:
            pass
        return
    
    ch = message.text.strip()
    data = load_data()
    if not ch.startswith('@'):
        bot.send_message(message.chat.id, '<b>⚠️ يجب أن يبدأ بـ @</b>', parse_mode='HTML')
        return
    if ch in data['channels']:
        bot.send_message(message.chat.id, '<b>⚠️ مضافة مسبقاً</b>', parse_mode='HTML')
        return
    data['channels'].append(ch)
    save_data(data)
    
    
    try:
        bot.delete_message(message.chat.id, msg_id)
    except:
        pass
    
    bot.send_message(message.chat.id, f'<b>✅ تمت الإضافة {ch}</b>', parse_mode='HTML')
    
    
    user_first_name = sanitize_text(message.from_user.first_name)
    user_username = sanitize_text(f"@{message.from_user.username}" if message.from_user.username else "بدون معرف")
    uid = str(message.from_user.id)
    
    welcome_message = f"""
<b>👋 أهلاً وسهلاً بك {user_first_name}</b>

<b>🆔 معرفك:</b> <code>{uid}</code>
<b>👤 اسم المستخدم:</b> {user_username}

<b>🦋 مرحباً بك في بوت ANES VIP ✅</b>
<b>اختر أحد الخيارات المتاحة ☃️</b>
"""
    show_main_menu(message.chat.id, True, welcome_message)

def do_add_admin(message, msg_id):
    
    if hasattr(message, 'data') and message.data.startswith('back|'):
        
        try:
            bot.delete_message(message.chat.id, msg_id)
        except:
            pass
        return
    
    aid = message.text.strip()
    data = load_data()
    if not aid.isdigit():
        bot.send_message(message.chat.id, '<b>⚠️ يجب أن يكون رقماً</b>', parse_mode='HTML')
        return
    
    for admin in data['admins']:
        if admin['id'] == aid:
            bot.send_message(message.chat.id, '<b>⚠️ مضاف مسبقاً</b>', parse_mode='HTML')
            return
    
    try:
        user_id = int(aid)
        chat = bot.get_chat(user_id)
        first_name = sanitize_text(chat.first_name)
        username = sanitize_text(f"@{chat.username}" if chat.username else "بدون معرف")
        
        data['admins'].append({
            'id': aid,
            'first_name': first_name,
            'username': username
        })
        save_data(data)
        
        
        try:
            bot.delete_message(message.chat.id, msg_id)
        except:
            pass
        
        bot.send_message(message.chat.id, f'<b>✅ أضيف مشرف {first_name} ({username})</b>', parse_mode='HTML')
        
        
        user_first_name = sanitize_text(message.from_user.first_name)
        user_username = sanitize_text(f"@{message.from_user.username}" if message.from_user.username else "بدون معرف")
        uid = str(message.from_user.id)
        
        welcome_message = f"""
<b>👋 أهلاً وسهلاً بك {user_first_name}</b>

<b>🆔 معرفك:</b> <code>{uid}</code>
<b>👤 اسم المستخدم:</b> {user_username}

<b>🦋 مرحباً بك في بوت ANES VIP</b>
<b>اختر أحد الخيارات المتاحة ☃️</b>
"""
        show_main_menu(message.chat.id, True, welcome_message)
    except Exception as e:
        data['admins'].append({
            'id': aid,
            'first_name': "غير معروف",
            'username': "بدون معرف"
        })
        save_data(data)
        
       
        try:
            bot.delete_message(message.chat.id, msg_id)
        except:
            pass
        
        bot.send_message(message.chat.id, f'<b>✅ أضيف مشرف جديد (ID: {aid})</b>\n\n<code>ملاحظة: لم يتم الحصول على معلومات المستخدم</code>', parse_mode='HTML')
        

        user_first_name = sanitize_text(message.from_user.first_name)
        user_username = sanitize_text(f"@{message.from_user.username}" if message.from_user.username else "بدون معرف")
        uid = str(message.from_user.id)
        
        welcome_message = f"""
<b>👋 أهلاً وسهلاً بك {user_first_name}</b>

<b>🆔 معرفك:</b> <code>{uid}</code>
<b>👤 اسم المستخدم:</b> {user_username}

<b>🦋 مرحباً بك في بوت Config App Dz 🏠</b>
<b>اختر أحد الخيارات المتاحة ☃️</b>
"""
        show_main_menu(message.chat.id, True, welcome_message)


if __name__ == '__main__':
    print('Bot is running...')
    bot.infinity_polling()
