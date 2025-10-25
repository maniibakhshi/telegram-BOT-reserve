import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from datetime import datetime
import time
import os
import logging
import jdatetime
from texts import *
from CONFIG import *
from DDL import *
from DML import *
from DQL import *



API_TOKEN = BOT_TOKEN
bot = telebot.TeleBot(API_TOKEN)
hideboard = ReplyKeyboardRemove()
logging.basicConfig(filename="project.log", level= logging.DEBUG,format="%(asctime)s - %(levelname)s - %(message)s", ) 
os.makedirs('receipts', exist_ok=True)
os.environ['TZ'] = 'Asia/Tehran'
time.tzset()


commands = {
    'start'             :   'منوی اصلی',
    'help'              :   'راهنما',

}

admin_commands = {
    'set_disable_hour_normal'   :   'غیر فعال کردن نوبت 1.5 ساعته',
    'set_disable_hour_groom'    :   'غیر فعال کردن نوبت 3 ساعته',
    'set_disable_hour_skin'     :   'غیر فعال کردن نوبت 3 ساعته',
    'set_amount_normal'         :   'تغییر مبلغ بیعانه نوبت عادی',
    'set_amount_groom'          :   'تغییر مبلغ بیعانه نوبت داماد',
    'set_amount_skin'           :   'تغییر مبلغ بیعانه نوبت پاکسازی پوست',
    'set_card'                  :   'تغییر شماره کارت ',
    'see_reserve_list'          :   'مشاهده لیست رزرو ',
    'see_reserve_weekly_list'   :   'مشاهده لیست رزرو هفتگی',
    'see_customer_list'         :   'مشاهده لیست مشتریان',
    'add_message'               :   'ارسال تبلیغات'
    
}

message_ids = {
    'reserve_select'    :    3,
    'sign_up'           :    4,
    'get_name'          :    5,
    'get_phone'         :    6,
    'name_error'        :    7,
    'phone_guide'       :    8,
    'phone_error'       :    9,
    'groom_guide'       :    10,
    'select_hour'       :    11,
    'send_receipt'      :    12,
    'wait_photo'        :    13,
    'approve'           :    14,
    'reject'            :    15,
    'wiat_admin'        :    16,
    'ask_amount'        :    17,
    'success_amount'    :    18,
    'add_message'       :    19

}
user_time = dict()
user_steps = dict() 
user_data = dict()
admin_steps = dict()
admin_data = dict()





def make_hour_keyboard(hours, date):
    keyboard = types.InlineKeyboardMarkup()
    
    for i in range(0, len(hours), 2):
        row_buttons = [
            types.InlineKeyboardButton(
                text=hour,
                callback_data=f"reserve|{hour}|{date}"
            )
            for hour in hours[i:i+2] 
        ]
        keyboard.row(*row_buttons)
    
    return keyboard


def start_registration(message):
    cid = message.chat.id
    bot.copy_message(cid, Channel_cid, message_ids['get_name'])
    bot.register_next_step_handler(message, get_name)
    

def get_name(message):
    cid = message.chat.id
    name = message.text.strip()

    if not name or len(name) < 3:
        bot.copy_message(cid, Channel_cid, message_ids['name_error'])
        bot.register_next_step_handler(message, get_name)
        return
    
    elif name == commands['start']:
        welcome()

    user_data[cid] = {"name": name}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    send_contact_btn = types.KeyboardButton(texts['send_phone'], request_contact=True)
    
    markup.add(send_contact_btn)
    

    bot.copy_message(cid, Channel_cid, message_ids['phone_guide'],reply_markup=markup)
    bot.register_next_step_handler(message, get_phone)


def get_phone(message):
    cid = message.chat.id
    username = message.from_user.username
    name = user_data[cid]['name']
    phone = None

    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone_text = message.text.strip()
        if phone_text.startswith("+98") or phone_text.startswith("09"):
            phone = phone_text
        else:
            bot.copy_message(cid, Channel_cid, message_ids['phone_error'])
            bot.register_next_step_handler(message, get_phone)
            return
    else:
        bot.copy_message(cid, Channel_cid, message_ids['phone_guide'])
        bot.register_next_step_handler(message, get_phone)
        return
    
    try:
        insert_data_users(cid, username, name, phone)
        logging.info(f"User: {cid}, name: {name}, phone:{phone} added to <users> table")
        bot.send_message(cid, texts['success'], reply_markup=types.ReplyKeyboardRemove())
        welcome(message)

    except Exception as e:
        logging.debug(f"error has occurred during register: {e}")
        bot.send_message(cid, texts['error'], reply_markup=hideboard)
        start_registration(message)

        




def send_payment_info(cid, name, date, hour):
    service = user_data[cid]['mode']
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(texts['send_photo'], callback_data=f"sendreceipt|{date}|{hour}"))

    try:
        res_id = save_data_reservation(cid, name, service, date, hour, 'pending')
        logging.info(f"name: {name} service: {service} date:{date} hour: {hour} successfully added to <{res_id}> reserve id")
        set_user_state(cid, 'send_card_number', res_id)
        bot.send_message(cid, f"{texts['pay']} \n \n {texts['reserve_amount']}: {get_amount(service)} تومان \n  {get_card()}  {texts['name1']}", parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        bot.send_message(cid, texts['error'], reply_markup=hideboard)
        logging.error(f'error has occurred during send_payment_info: {e}', exc_info=True)
        
        
#---------------------------------- admin functions ---------------------------------
def make_hour_admin_keyboard(hours, date, mode='normal'):
    keyboard = types.InlineKeyboardMarkup()
    
    
    for i in range(0, len(hours), 2):
        row_buttons = [
            types.InlineKeyboardButton(text=hour,callback_data=f"disable|{hour}|{date}|{mode}")
            for hour in hours[i:i+2] 
        ]
        keyboard.row(*row_buttons)
    
    return keyboard


def notif_admin_payment(cid, photo_path, res_id):
    try:
        detail = get_reseve_detail(res_id)
        name = detail[0]
        service = detail[1]
        date = detail[2]
        sec_time = detail[3]
        hour = (jdatetime.datetime(1,1,1)+sec_time).strftime("%H:%M")
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(texts['approve'], callback_data=f"approve|{res_id}|{date}|{hour}"),
            InlineKeyboardButton(texts['reject'], callback_data=f"reject|{res_id}|{date}|{hour}")
        )
        text = (
        f"👤 *{name}*\n"
        f"💈 *{texts[service]}*\n"
        f"📅 {date} | 🕒 {hour}\n"
        "───────────────\n")
        photo = open(photo_path, 'rb')
        bot.send_photo(admins, photo, caption=text, reply_markup=markup, parse_mode="Markdown")
        logging.info(f'payment detail reserve id:{res_id} succussfully sent to admin')
    except Exception as e:
        bot.send_message(cid, texts['error'])
        logging.warning(f'failed send PAYMENT INFO reserve id: {res_id} to admin', exc_info=True)


def notif_admin_new_reserve(res_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(texts['see_list'], callback_data= 'show_reserve|all'), InlineKeyboardButton(texts['see_detail'], callback_data=f'show_reserve|detail|{res_id}'))
    bot.send_message(admins, texts['new_reserve'], reply_markup=markup)



def get_new_card(message):
    cid = message.chat.id
    bot.send_message(cid, texts['set_card'])
    bot.register_next_step_handler(message, set_new_card)


def set_new_card(message):
    cid = message.chat.id
    if cid != admins:
        return
    
    try:
        number = message.text.strip()
        set_card(number)
        logging.warning(f'NEW CARD NUMBER ADDED: {number}')
        bot.send_message(cid, texts['success_card'])
    except Exception:
        bot.send_message(cid, texts['try_again'])
        logging.error('FAILED ADDING NEW CARD NUMBER', exc_info=True)
    


def get_new_amount(message):
    cid = message.chat.id
    bot.copy_message(cid, Channel_cid, message_ids['ask_amount'])
    bot.register_next_step_handler(message, set_new_amount)

def set_new_amount(message):
    cid = message.chat.id
    if cid != admins:
        return
    
    try:
        amount = message.text.strip()
        mode = admin_data['amount_mode']
        set_amount(amount, mode)
        bot.copy_message(cid, Channel_cid, message_ids['success_amount'])
        logging.warning(f'NEW AMOUNT {amount} added in service: {mode}')
    except Exception as e:
        bot.send_message(cid, texts['try_again'])
        logging.error(f'FAILED TO SET NEW AMOUNT: {e}', exc_info=True)

def get_add_message(message):
    cid = message.chat.id
    bot.copy_message(cid, Channel_cid, message_ids['add_message'])
    bot.register_next_step_handler(message, send_add_message)

def send_add_message(message):
    cid = message.chat.id
    if cid != admins:
        return
    try:
        text = message.text
        id_list = get_ids()
        id_count = len(id_list)
        
        for id in id_list:
            bot.send_message(id, text)
        bot.send_message(cid, f"{texts['success_message']} {id_count} {texts['success_message2']}")


    except Exception:
        bot.send_message(cid, texts['try_again'])
    


def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            logging.info(f"{m.chat.first_name} [{m.chat.id}]: {m.text}")
        elif m.content_type == 'photo':
            logging.info(f"{m.chat.first_name} [{m.chat.id}]: New photo recieved")
        elif m.content_type == 'document':
            logging.info(f"{m.chat.first_name} [{m.chat.id}]: New document recieved, filename: {m.document.filename}")
        else:
            logging.info(f"{m.chat.first_name} [{m.chat.id}]: another content recieved: {m.content_type}")
            

bot.set_update_listener(listener)


#---------------------------- call back query handler -------------------------------

@bot.callback_query_handler(func= lambda call: call.data == 'back')
def back_handler(call):
    call_id = call.id
    cid = call.message.chat.id
    mid = call.message.message_id

    bot.answer_callback_query(call_id, texts['back'])
    bot.edit_message_reply_markup(cid,mid,reply_markup=None)
    welcome(call.message)





@bot.callback_query_handler(func=lambda call: call.data.startswith(('reserve', 'confirm')))
def payment(call):
    call_id = call.id
    cid = int(call.message.chat.id)
    name = get_user_detail(int(cid))[0]
    #if is_spam(cid): return
    mid = call.message.message_id
    text = call.data.split('|')
    
    hour, date = text[1::]
    if text[0] == 'reserve':
        bot.answer_callback_query(call_id, texts['success_hour'])
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts['q_confirm'], callback_data=f'confirm|{hour}|{date}'), InlineKeyboardButton(texts['back'], callback_data='back'))
        bot.edit_message_text(f"{date}  |  {hour} {texts['selected_date']} ", cid, mid, reply_markup=markup)
        

    elif text[0] == 'confirm':
        bot.answer_callback_query(call_id, texts['success_reserve'])
        bot.edit_message_text(f"{texts['date']}: {date}   {texts['hour']}: {hour} \n {texts['success_reserve']}", cid, mid, reply_markup=None)
        send_payment_info(cid, name, date, hour)


@bot.callback_query_handler(func=lambda call: call.data.startswith('sendreceipt'))
def send_receipt(call):
    call_id = call.id
    cid = call.message.chat.id
    #if is_spam(cid): return
    mid = call.message.message_id
    
    bot.edit_message_reply_markup(cid, mid, reply_markup=None)
    bot.answer_callback_query(call_id, texts['send_receipt'])
    user_steps[cid] = 'WAIT_FOR_RECEIPT'
    bot.copy_message(cid, Channel_cid, message_ids['send_receipt'])



@bot.callback_query_handler(func=lambda call: call.data.startswith(('approve', 'reject')))
def approve_reserve(call):
    call_id = call.id
    cid = call.message.chat.id
    action, res_id, date, time = call.data.split('|')
    user_id = get_reseve_detail(res_id)[-1]
    service = get_reseve_detail(res_id)[1]
    keyboard = ReplyKeyboardMarkup()
    keyboard.add(texts['back'])
    if cid != admins:
        welcome(call.message)
        return

    if action == 'approve':
        bot.answer_callback_query(call_id, texts['approve_pay'])

        try:
            if service == 'normal':
                insert_disable_hour(date, time)
                logging.info(f"date: {date} hour: {time} successfully disabled with reserve id: {res_id}")
            elif service == 'groom' or service == 'skin':
                new_time = jdatetime.datetime.strptime(time, "%H:%M")
                next_time = new_time + timedelta(minutes=90)
                insert_disable_hour(date, time)
                insert_disable_hour(date, next_time)
                logging.info(f"date: {date} hour: {time}{next_time} successfully disabled with reserve id: {res_id}")

            update_reservations(res_id, 'paid')
            logging.info(f"reserve id: {res_id} successfully UPDATED <RESERVATIONS> table to <paid>")
            update_transactions(res_id, 'success')
            logging.info(f"reserve id: {res_id} successfully UPDATED <TRANSACTIONS> table to <success>")
            user_steps.pop(cid, None)
            user_data.pop(cid, None)
            user_time.pop(cid, None)
            bot.copy_message(user_id, Channel_cid, message_ids['approve'], reply_markup=keyboard)
            notif_admin_new_reserve(res_id)
            clear_user_state(cid)
            logging.info(f'successfully clearing <USER_STATE> user id: {cid}', exc_info=True)


        except Exception as e:
            bot.send_message(cid, texts['error'])
            logging.error(f"error has ocurred during APPROVE RESERVE due to: {e}")
            welcome(call.message)

        

    elif action == 'reject':
        bot.answer_callback_query(call_id, texts['reject_pay'])
        try:
            update_reservations(res_id, 'failed')
            logging.info(f"reserve id: {res_id}  REJECTED <RESERVATIONS> table to <failed>")
            update_transactions(res_id, 'failed')
            logging.info(f"reserve id: {res_id}  REJECTED <TRANSACTIONS> table to <failed>")
            user_steps.pop(cid, None)
            user_data.pop(cid, None)
            user_time.pop(cid, None)
            bot.copy_message(user_id, Channel_cid, message_ids['reject'], reply_markup=keyboard)
            clear_user_state(cid)
        except Exception as e:
            bot.send_message(cid, texts['error'])
            logging.error(f"error has ocurred during REJECT RESERVE due to: {e}")
            welcome(call.message)
        




#---------------------------------- admin call back query ---------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('show_reserve'))
def show_admin(call):
    cid = call.message.chat.id
    call_id = call.id
    text = call.data.split('|')
    action = text[1]
    
    if cid != admins:
        return
    else:

        if action == 'detail':
            bot.answer_callback_query(call_id, texts['see_detail'])
            rse_id = text[-1] 
            reservee_data = get_reseve_detail(rse_id)
            name = reservee_data[0]
            service = reservee_data[1]
            date = reservee_data[2]
            time = reservee_data[3]
            user_id = reservee_data[4]
            phone = get_user_detail(user_id)[1]

            text = '📋 *جزییات رزرو:*\n\n'
            text += (
        f"👤 *{name}*\n"
        f"📅 {date} | 🕒 {time}\n"
        f"💈 {service} | 📞 {phone}\n"
        "───────────────\n")

            bot.send_message(cid, text, parse_mode="Markdown")

        elif action == 'all':
            bot.answer_callback_query(call_id, texts['see_list'])
            list = get_reserve_list()
            text = '📋 *لیست رزروهای فعال:*\n\n'
            for i in list:
                name = i[0]
                service = i[1]
                date = i[2]
                time = i[3]
                phone = get_user_detail(i[4])[1]
                text += (
        f"👤 *{name}*\n"
        f"📅 {date} | 🕒 {time}\n"
        f"💈 {service} | 📞 {phone}\n"
        "───────────────\n")
            bot.send_message(cid, text, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith('disable'))
def disable_time(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    text = call.data.split('|')
    mode = text[3]
    date = jdatetime.datetime.strptime(text[2], '%Y-%m-%d')
    hour = jdatetime.datetime.strptime(text[1], '%H:%M')
    if cid != admins:
        return
    
    try:
        if mode == 'normal':
            insert_disable_hour(date, hour)
            logging.info(f"ADMIN DISABLED date: {date} hour: {hour}")
        elif mode in ['groom', 'skin']:
                next_time = hour + timedelta(minutes=90)
                insert_disable_hour(date, hour)
                insert_disable_hour(date, next_time)
                logging.info(f"ADMIN DISABLED date: {date} hour: {hour} {next_time}")

        admin_steps.pop(cid, None)
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        bot.send_message(cid, f"{text[1]} {texts['success_disable']}")
    except Exception as e:
        bot.send_message(cid, texts['error'])
        logging.error(f"ADMIN FAILED TO DISABLE: {e}", exc_info=True)
        welcome(call.message)



#---------------------------------- message handler ---------------------------------



@bot.message_handler(commands=['start'])
def welcome(message):
    cid = message.chat.id
    insert_id(cid)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(texts['reserve'])
    keyboard.add(texts['groom_reserve'])
    keyboard.add(texts['skin_reserve'])
    keyboard.add(texts['panel'])
    
    bot.send_message(cid, texts['menu'], reply_markup=keyboard)
    

@bot.message_handler(commands=['help'])
def command_help(message):
    cid = message.chat.id
    help_text = "دستورات زیر فعال است: \n"
    for key in commands: 
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    if cid == admins:
        help_text += "*********دستورات ادمین**********\n"
        for key in admin_commands:  
            help_text += "/" + key + ": "
            help_text += admin_commands[key] + "\n"
    bot.send_message(cid, help_text)  





@bot.message_handler(func=lambda    message: message.text == texts['back'])
def back(message):
    welcome(message)


@bot.message_handler(func=lambda message: message.text == texts['panel'])
def panel(message):
    cid = message.chat.id
    try:
        result = get_user_detail(cid)
        name = result[0]
        phone = result[1]
        bot.send_message(cid, f"{texts['name']}: {name} \n {texts['phone']}: {phone}")
    except Exception:
        bot.send_message(cid, texts['not_found'])



@bot.message_handler(func=lambda message: message.text == texts['reserve'])
def reserve(message, mode='normal'):
    cid = message.chat.id

    user_time[cid] = {}

    user_status = check_user(cid)
    if user_status == None:
        bot.copy_message(cid, Channel_cid, message_ids['sign_up'], reply_markup=hideboard)
        start_registration(message)
        return
    
    bot.copy_message(cid, Channel_cid, message_ids['reserve_select'], reply_markup=hideboard)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    if mode == 'groom':
        minimum_date = jdatetime.date.today() + jdatetime.timedelta(days=5)
    elif mode in ['normal', 'skin']:
        minimum_date = jdatetime.date.today()

    for i in range(1, 20):
        day = minimum_date + jdatetime.timedelta(days=i)
        weekday = weekdays_fa[day.weekday()]
        month = months_fa[day.month - 1]
        if weekday == 'جمعه':
            continue

        text = f'{weekday}  {day.day} {month}'
        buttons.append(types.KeyboardButton(text))
        user_time[cid][text] = day.togregorian()

    buttons.append(types.KeyboardButton(texts['back']))

    for i in range(0, len(buttons), 2):
        keyboard.row(*buttons[i:i+2])
    

    bot.copy_message(cid, Channel_cid, message_ids['groom_guide'], reply_markup=keyboard)
    user_steps[cid] = 'RESERVE'
    user_data[cid] = {'mode': mode}



@bot.message_handler(func=lambda message: message.text == texts['groom_reserve'])
def groom_reserve(message):
    reserve(message, 'groom')



@bot.message_handler(func=lambda message: message.text == texts['skin_reserve'])
def skin_reserve(message):
    reserve(message, 'skin')



@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'RESERVE')
def reserve_hour(message):
    cid = message.chat.id
    text = message.text
    user_date = user_time[cid][text]
    selected_date =  jdatetime.date.fromgregorian(date=user_date).strftime("%Y-%m-%d") 
    
    del user_time[cid]
    bot.send_message(cid, f"{texts['selected']}: {text}", reply_markup=hideboard)
    
    if user_data[cid]['mode'] == 'normal':
        open_hours = get_hours(selected_date)
    elif user_data[cid]['mode'] in ['groom', 'skin']:
        open_hours = get_hours(selected_date, 'groom')
    
    markup = make_hour_keyboard(open_hours, selected_date)
    bot.copy_message(cid, Channel_cid, message_ids['select_hour'], reply_markup=markup)
    user_steps[cid] = 'P'
                                    

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    cid = message.chat.id
    user_state = get_state(cid)
    if user_steps.get(cid) != 'WAIT_FOR_RECEIPT':
        return

    res_id = user_state[2]
    file_id = message.photo[-1].file_id
    try:
        file_info = bot.get_file(file_id) 
        downloaded = bot.download_file(file_info.file_path)
        save_path = f"receipts/{cid}_{file_id}.jpg"

        with open (save_path, 'wb') as f:
            f.write(downloaded)
        logging.info(f"file id {file_id} SUCCESSFULLY DOWNLOADED")

        resreve_detail = get_reseve_detail(res_id)
        name = resreve_detail[0]
        amount = get_amount(resreve_detail[1])
        seve_transaction_card(cid, name, res_id, amount, 'card_to_card', file_id, 'pending')
        logging.info(f"reserve id {res_id} saved to <TRANSACTIONS> in status: <PENDING>")
        bot.copy_message(cid, Channel_cid, message_ids['wait_photo'])
        notif_admin_payment(cid, save_path, res_id)
        user_steps.pop(cid, None)
    except Exception as e:
        bot.send_message(cid, texts['error'])
        logging.error(f"error has ocurred during HANDLE RECEIPT due to: {e}", exc_info=True)
        


#----------------------------------admin  message handler ---------------------------------
@bot.message_handler(commands=['set_disable_hour_normal'])
def selct_disable_date(message, mode='normal'):
    cid = message.chat.id
    if cid == admins:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []
        minimum_date = jdatetime.date.today()

        for i in range(1, 30):
            day = minimum_date + jdatetime.timedelta(days=i)
            weekday = weekdays_fa[day.weekday()]
            month = months_fa[day.month - 1]
            if weekday == 'جمعه':
                continue

            text = f'{weekday}  {day.day} {month}'
            buttons.append(types.KeyboardButton(text))
            admin_data[text] = day.togregorian()
        buttons.append(types.KeyboardButton(texts['back']))

        for i in range(0, len(buttons), 2):
            keyboard.row(*buttons[i:i+2])

        bot.send_message(cid, texts['select_date'], reply_markup=keyboard)
        admin_steps[cid] = 'SET_DISABLE_HOUR'
        admin_data['mode'] = mode


@bot.message_handler(commands=['set_disable_hour_groom'])
def selct_disable_date_groom(message):
    selct_disable_date(message, 'groom')

@bot.message_handler(commands=['set_disable_hour_skin'])
def selct_disable_date_skin(message):
    cid = message.chat.id
    if cid == admins:
        selct_disable_date_groom(message)


@bot.message_handler(commands=['set_card'])
def ask_new_card(message):
    cid = message.chat.id
    if cid != admins:
        return
    get_new_card(message)


@bot.message_handler(commands=['set_amount_normal'])
def ask_normal_amount(message):
    cid = message.chat.id
    if cid != admins:
        return
    get_new_amount(message)
    
@bot.message_handler(commands=['set_amount_groom'])
def ask_groom_amount(message):
    cid = message.chat.id
    if cid != admins:
        return
    admin_data['amount_mode'] = 'groom'
    get_new_amount(message)
    

@bot.message_handler(commands=['set_amount_skin'])
def ask_skin_amount(message):
    cid = message.chat.id
    if cid != admins:
        return
    admin_data['amount_mode'] = 'skin'
    get_new_amount(message)
    

@bot.message_handler(commands=['see_reserve_list'])
def reserve_list(message, mode='daily'):
    cid = message.chat.id

    if cid != admins:
        return
    
    try:
        if mode == 'daily':
            list = get_reserve_list()
        elif mode == 'weekly':
            list = get_reserve_weekly_list()
    except Exception as e:
        bot.send_message(cid, texts['error'])
        logging.error(f"error has ocurred during GET RESERVE LIST: {e}", exc_info=True)
        

    text = '📋 *لیست رزروهای فعال:*\n\n'
    for i in list:
            name = i[0]
            service = i[1]
            date = i[2]
            time = i[3]
            phone = get_user_detail(i[4])[1]
            text += (
        f"👤 *{name}*\n"
        f"📅 {date} | 🕒 {time}\n"
        f"💈 {service} | 📞 {phone}\n"
        "───────────────\n")
    bot.send_message(cid, text, parse_mode="Markdown")

@bot.message_handler(commands=['see_reserve_weekly_list'])
def reserve_weekly_list(message):
    cid = message.chat.id

    if cid != admins:
        return
    reserve_list(message, 'weekly')

    
@bot.message_handler(commands=['see_customer_list'])
def send_costumer_list(message):
    cid = message.chat.id

    if cid != admins:
        return
    
    list = get_costumer_list()
    text = '📋 *لیست مشتریان:*\n\n'
    for i in list:
        name = i[0]
        username = i[1]
        phone = i[2]
        text += (
        f"👤 {name}\n"
        f"🆔 {username} \n 📞 {phone}\n"
        "───────────────\n")
    bot.send_message(cid, text)

@bot.message_handler(commands=['add_message'])
def ask_message(message):
    cid = message.chat.id

    if cid != admins:
        return
    
    get_add_message(message)

@bot.message_handler(func=lambda message: admin_steps.get(message.chat.id) == 'SET_DISABLE_HOUR')
def set_disable_hour(message):
    cid = message.chat.id
    text = message.text
    if cid == admins:
        admin_date = admin_data[text]
        selected_date =  jdatetime.date.fromgregorian(date=admin_date).strftime("%Y-%m-%d") 
        bot.send_message(cid, f"{texts['selected']}: \n {selected_date}", reply_markup=hideboard)
        
        try:
            if admin_data['mode'] == 'normal':
                open_hours = get_hours(selected_date)
                admin_markup = make_hour_admin_keyboard(open_hours, selected_date)
            elif admin_data['mode'] in ['groom', 'skin']:
                open_hours = get_hours(selected_date, 'groom')
                admin_markup = make_hour_admin_keyboard(open_hours, selected_date, admin_data['mode'])
            
            bot.copy_message(cid, Channel_cid, message_ids['select_hour'], reply_markup=admin_markup)
        except Exception as e:
            logging.error(f"error in sending disable date list: {e}")
            bot.send_message(cid, texts['error'])
            
    



if __name__ == "__main__":
    bot.infinity_polling()

            
            
       
