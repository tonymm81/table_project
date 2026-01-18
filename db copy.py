import json
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # olemassa oleva devices-taulu
    cur.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_key VARCHAR(255) PRIMARY KEY,
            value_json TEXT NOT NULL
        )
    """)
    # uusi taulu käyttäjätallennuksille
    cur.execute("""
        CREATE TABLE IF NOT EXISTS saved_configs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            save_key VARCHAR(255) NOT NULL UNIQUE,
            slot_index INT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            value_json LONGTEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Tallennusfunktio: lisää tai päivitä tallennus
def save_config(save_key: str, value: dict, slot_index: int = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "REPLACE INTO saved_configs (save_key, slot_index, value_json) VALUES (%s, %s, %s)",
            (save_key, slot_index, json.dumps(value, ensure_ascii=False))
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Latausfunktio: hae tallennus avaimella
def load_config(save_key: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT value_json FROM saved_configs WHERE save_key=%s", (save_key,))
        row = cur.fetchone()
        if not row or not row.get('value_json'):
            return None
        raw = row['value_json']
        # jos raw on jo dict (harvinainen), palauta suoraan
        if isinstance(raw, dict):
            return raw
        try:
            return json.loads(raw)
        except Exception:
            # yritä palauttaa raw sellaisenaan jos se on jo dict-tyyppinen stringi
            return None
    finally:
        conn.close()

# Listaa tallennukset (avain, slot, päivitetty)
def list_configs():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT save_key, slot_index, updated_at FROM saved_configs ORDER BY updated_at DESC")
        return cur.fetchall()
    finally:
        conn.close()
