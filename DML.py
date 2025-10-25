import mysql.connector
from CONFIG import *
from datetime import timedelta, datetime
import time
os.environ['TZ'] = 'Asia/Tehran'
time.tzset()



def insert_id(telegram_id):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute('''
INSERT INTO advertise_ids (telegram_id)
      VALUES (%s)
      ON DUPLICATE KEY UPDATE telegram_id = VALUES(telegram_id)''', (telegram_id,)
      )
     conn.commit()
     cur.close()
     conn.close()
     





def insert_data_users(telegram_id, telegram_username, name, phone):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute('''
INSERT INTO users (telegram_id, telegram_username, name, phone)
      VALUES (%s, %s, %s, %s)''', (telegram_id, telegram_username, name, phone))
     conn.commit()
     cur.close()
     conn.close()
     



#service ENUM('normal', 'groom', 'skin')
def save_data_reservation(cid, name, service, date, time, status='pending'):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute('''
INSERT INTO reservations (user_id, name, service, date, time, payment_status)
      VALUES (%s, %s, %s, %s, %s, %s)''', (cid, name, service, date, time, status))
     reservation_id = cur.lastrowid

     conn.commit()
     cur.close()
     conn.close()

     
     return reservation_id



#method ENUM('gateway','card_to_card')
#status ENUM('pending','success','failed')
def seve_transaction_card(cid, name, reservation_id, amount, method, photo_path, status):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute('''
INSERT INTO transactions (user_id, name, reservation_id, amount, method, photo_path, status)
      VALUES (%s, %s, %s, %s, %s, %s, %s)''', (cid, name, reservation_id, amount, method, photo_path, status))
     conn.commit()
     cur.close()
     conn.close()

     







def insert_default_hours():
     start_time = datetime.strptime("11:00", "%H:%M")
     end_time = datetime.strptime("23:00", "%H:%M")
     slot = timedelta(minutes=90)

     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()


     
     t = start_time
     while t + slot <= end_time:
          start_str = t.time().strftime("%H:%M")
          cur.execute(
                    "INSERT IGNORE INTO default_hours (time) VALUES (%s)",
                    (start_str,)
               )
          t = t + slot

     conn.commit()
     cur.close()
     conn.close()
     


def insert_disable_hour(date, time):
     conn = mysql.connector.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""
INSERT INTO disabled_hours (date, time)
VALUES (%s, %s)
""", (date, time))
     
     conn.commit()
     cur.close()
     conn.close()


def set_card(value):
     conn = mysql.connector.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""
INSERT INTO settings (key_name, value)
VALUES ('card_number', %s)
ON DUPLICATE KEY UPDATE value = VALUES(value)
""", (value,))
     conn.commit()
     cur.close()
     conn.close()

     return True

def set_amount(value, mode='normal'):
     text = f'amount_{mode}'
     conn = mysql.connector.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""
INSERT INTO settings (key_name, value)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE value = VALUES(value)
""", (text, value))
     conn.commit()
     cur.close()
     conn.close()

     return True

def set_user_state(user_id, state, reservation_id):
     conn = mysql.connector.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""
INSERT INTO user_states (user_id, state, reservation_id)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE
                 state = VALUES(state),
                 reservation_id = VALUES(reservation_id)
""", (user_id, state, reservation_id))
     conn.commit()
     cur.close()
     conn.close()
     
def clear_user_state(cid):
     conn = mysql.connector.connection.MySQLConnection(**config)
     cur = conn.cursor()

     cur.execute("""DELETE FROM user_states WHERE user_id = %s """, (cid,))
     
     conn.commit()
     conn.close()
     cur.close()
     


def update_reservations(res_id, status):
     conn = mysql.connector.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""
UPDATE reservations SET payment_status=%s WHERE id=%s
""", (status, res_id))
     conn.commit()
     cur.close()
     conn.close()

def update_transactions(res_id, status):
     conn = mysql.connector.MySQLConnection(**config)
     cur = conn.cursor()
     cur.execute("""
UPDATE transactions SET status=%s WHERE id=%s
""", (status, res_id))
     conn.commit()
     cur.close()
     conn.close()

if __name__ == "__main__":
     insert_default_hours()
     