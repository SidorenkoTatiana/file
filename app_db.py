import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from typing import Optional, Dict

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def authenticate_user(login: str, password: str) -> Optional[Dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, login, role, full_name FROM users WHERE login = %s AND password_hash = crypt(%s, password_hash)",
                (login, password)
            )
            user = cursor.fetchone()
            if user:
                return {
                    'user_id': user[0],
                    'login': user[1],
                    'role': user[2],
                    'full_name': user[3]
                }
            return None
    finally:
        conn.close()

# Дополнительные функции работы с БД...
