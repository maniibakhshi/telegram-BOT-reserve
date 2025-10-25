import mysql.connector
from CONFIG import *
import os, time

os.environ['TZ'] = 'Asia/Tehran'
time.tzset()


def set_zone():
    conn = mysql.connector.MySQLConnection(user=config['user'], password=config['password'], host=config['host'])
    cur = conn.cursor()
    cur.execute("SET time_zone = '+03:30'")
    conn.commit()
    cur.close()
    conn.close()

def create_n_drop_database(db_name):
    conn = mysql.connector.MySQLConnection(user=config['user'], password=config['password'], host=config['host'])
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
    conn.commit()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Database '{db_name}' created successfully!")



def create_table_advertise_ids():
    conn = mysql.connector.MySQLConnection(**config)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE advertise_ids (
        id INT AUTO_INCREMENT PRIMARY KEY,
        telegram_id BIGINT NOT NULL,
        UNIQUE KEY uq_users_telegram (telegram_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """)
    conn.commit()
    cur.close()
    conn.close()



def create_table_users():
    conn = mysql.connector.MySQLConnection(**config)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        telegram_id BIGINT NOT NULL,
        telegram_username VARCHAR(100) NULL,
        name VARCHAR(100),
        phone VARCHAR(15),
        role ENUM('user','admin') NOT NULL DEFAULT 'user',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_users_telegram (telegram_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """)
    conn.commit()
    cur.close()
    conn.close()


def create_table_reservations():
    conn = mysql.connector.MySQLConnection(**config)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE reservations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        name VARCHAR(50) NOT NULL,
        service ENUM('normal','groom', 'skin') NOT NULL DEFAULT 'normal',
        date DATE NOT NULL,
        time TIME NOT NULL,
        payment_status ENUM('pending','paid','failed') NOT NULL DEFAULT 'pending',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        CONSTRAINT fk_res_user FOREIGN KEY (user_id)
            REFERENCES users(telegram_id) ON DELETE CASCADE ON UPDATE CASCADE,
        INDEX idx_res_date_time (date, time),
        INDEX idx_res_user (user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_table_transactions():
    conn = mysql.connector.MySQLConnection(**config)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        name VARCHAR(50) NOT NULL,
        reservation_id INT NULL,
        amount varchar(50) NOT NULL,
        method ENUM('gateway','card_to_card') NOT NULL,
        photo_path VARCHAR(250) NULL,
        reference_code VARCHAR(255),
        status ENUM('pending','success','failed') NOT NULL DEFAULT 'pending',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
        CONSTRAINT fk_tx_user FOREIGN KEY (user_id)
            REFERENCES users(telegram_id) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT fk_tx_res FOREIGN KEY (reservation_id)
            REFERENCES reservations(id) ON DELETE SET NULL ON UPDATE CASCADE,
        INDEX idx_tx_user (user_id),
        INDEX idx_tx_res (reservation_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """)
    conn.commit()
    cur.close()
    conn.close()


def create_table_default_hours():
    conn = mysql.connector.MySQLConnection(**config)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE default_hours (
        id INT AUTO_INCREMENT PRIMARY KEY,
        time TIME NOT NULL,
        UNIQUE KEY unique_time (time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_table_disabled_hours():
    conn = mysql.connector.MySQLConnection(**config)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE disabled_hours (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE NOT NULL,
        time TIME NOT NULL,
        UNIQUE KEY unique_date_time (date, time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_table_settings():
    conn = mysql.connector.MySQLConnection(**config)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE settings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        key_name VARCHAR(50) UNIQUE NOT NULL,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_table_user_states():
    conn = mysql.connector.MySQLConnection(**config)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE user_states (
        user_id BIGINT PRIMARY KEY,
        state VARCHAR(50) NOT NULL,
        reservation_id INT DEFAULT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_all_tables():
    set_zone()
    create_n_drop_database(databasename)
    create_table_advertise_ids()
    create_table_users()
    create_table_reservations()
    create_table_transactions()
    create_table_default_hours()
    create_table_disabled_hours()
    create_table_settings()
    create_table_user_states()
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    create_all_tables()