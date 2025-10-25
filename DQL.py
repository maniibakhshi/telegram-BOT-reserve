import mysql.connector
from CONFIG import *
import time
from datetime import datetime, timedelta
import jdatetime
os.environ['TZ'] = 'Asia/Tehran'
time.tzset()


def get_ids():
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute('SELECT telegram_id FROM advertise_ids')
     result = cur.fetchall()
     conn.commit()
     conn.close()
     cur.close()
     ids = []
     for i in result:
          ids.append(i[0])
     return ids



def check_user(id):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute('SELECT id FROM USERS WHERE telegram_id = %s', (id,))
     result = cur.fetchone()
     conn.commit()
     conn.close()
     cur.close()
     return result




def get_hours(date, mode='normal'):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     query = '''SELECT TIME_FORMAT (time, '%H:%i')  FROM default_hours WHERE time NOT IN 
                 (SELECT time FROM disabled_hours WHERE date = %s) ORDER BY time ASC;'''
     
     cur.execute(query,[date])
     hours = [row[0] for row in cur.fetchall()]
     conn.commit()
     conn.close()
     cur.close()


     if mode == 'groom' or mode == 'skin':
          valid_hours = []
          for i in range(0, len(hours)-1):
               h1 = datetime.strptime(hours[i], "%H:%M")
               h2 = datetime.strptime(hours[i+1], "%H:%M")

               diff = (h2 - h1).total_seconds()/60
               
               if diff == 90:
                    valid_hours.append(hours[i])
          return valid_hours
     return hours
    



def get_card():
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""SELECT value FROM settings WHERE key_name = %s """, ('card_number',))
     result = cur.fetchone()

     conn.commit()
     conn.close()
     cur.close()

     if result and result[0]:
          return result[0]
     
     return default_card




def get_amount(mode='normal'):
     text = f'amount_{mode}'
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""SELECT value FROM settings WHERE key_name = %s """, (text,))
     result = cur.fetchone()

     conn.commit()
     conn.close()
     cur.close()


     if result and result[0]:
          return result[0]
     elif mode == 'normal':
          return default_amount
     elif mode == 'groom':
          return groom_amount
     elif mode == 'skin':
          return skin_amount




def get_state(cid):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()

     cur.execute("""SELECT * FROM user_states WHERE user_id = %s """, (cid,))
     row = cur.fetchone()

     conn.commit()
     conn.close()
     cur.close()
     
     return row

     





def get_user_detail(cid):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""SELECT name, phone FROM users WHERE telegram_id = %s """, (cid,))
     result = cur.fetchone()
     conn.commit()
     conn.close()
     cur.close()
     return result




def get_reseve_detail(res_id):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""SELECT name, service, date, time, user_id FROM reservations WHERE id = %s """, (res_id,))
     result = cur.fetchone()

     conn.commit()
     conn.close()
     cur.close()

     return result




def get_reserve_list():
     today=jdatetime.date.today()
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""SELECT name, service, date, time, user_id FROM reservations WHERE date >= %s and payment_status = 'paid' """, (today,))
     result = cur.fetchall()
     conn.commit()
     conn.close()
     cur.close()
     return result

def get_reserve_weekly_list():
     today=jdatetime.date.today()
     week = today + jdatetime.timedelta(days=7)
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""SELECT name, service, date, time, user_id FROM reservations WHERE date <= %s and payment_status = 'paid' """, (week,))
     result = cur.fetchall()
     conn.commit()
     conn.close()
     cur.close()
     return result

def get_costumer_list():
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""SELECT name, telegram_username, phone FROM users; """)
     result = cur.fetchall()
     conn.commit()
     conn.close()
     cur.close()
     return result

