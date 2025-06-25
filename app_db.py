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
def get_invoices_by_type_and_date(invoice_type, date):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT i.invoice_number, i.creation_date, COUNT(pi.parcel_id) as parcel_count
                FROM invoices i
                LEFT JOIN parcel_invoice pi ON i.invoice_id = pi.invoice_id
                WHERE i.invoice_type = %s AND DATE(i.creation_date) = %s
                GROUP BY i.invoice_number, i.creation_date
                ORDER BY i.creation_date DESC
            """, (invoice_type, date))
            return [{
                'invoice_number': row[0],
                'creation_date': row[1],
                'parcel_count': row[2]
            } for row in cursor.fetchall()]
    finally:
        conn.close()

def get_parcels_by_status(status):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.* FROM parcels p
                WHERE p.status = %s
                ORDER BY p.arrival_date
            """, (status,))
            return [{
                'parcel_id': row[0],
                'track_number': row[1],
                'internal_number': row[2],
                'sender': row[3],
                'recipient': row[4],
                'status': row[5],
                'arrival_date': row[6],
                'delivery_date': row[7],
                'region_code': row[9]
            } for row in cursor.fetchall()]
    finally:
        conn.close()

def update_parcel_status(parcel_id, status, user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE parcels
                SET status = %s, last_status_change = NOW(), last_updated_by = %s
                WHERE parcel_id = %s
                RETURNING parcel_id
            """, (status, user_id, parcel_id))
            conn.commit()
            return cursor.fetchone()[0]
    finally:
        conn.close()

def generate_delivery_list(manager_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("generate_delivery_list", (manager_id,))
            invoice_id = cursor.fetchone()[0]
            conn.commit()
            return invoice_id
    finally:
        conn.close()

def get_parcels_for_invoice(invoice_number):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.* FROM parcels p
                JOIN parcel_invoice pi ON p.parcel_id = pi.parcel_id
                JOIN invoices i ON pi.invoice_id = i.invoice_id
                WHERE i.invoice_number = %s
                ORDER BY p.internal_number
            """, (invoice_number,))
            return [{
                'parcel_id': row[0],
                'track_number': row[1],
                'internal_number': row[2],
                'sender': row[3],
                'recipient': row[4],
                'status': row[5],
                'arrival_date': row[6],
                'delivery_date': row[7],
                'region_code': row[9]
            } for row in cursor.fetchall()]
    finally:
        conn.close()

def add_parcels_to_office(parcels, user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for parcel in parcels:
                cursor.execute("""
                    INSERT INTO parcels (
                        track_number, sender, recipient, status, 
                        arrival_date, last_status_change, region_code, last_updated_by
                    ) VALUES (
                        %s, %s, %s, 'delivered_to_office', 
                        NOW(), NOW(), %s, %s
                    )
                """, (
                    parcel['track_number'],
                    parcel['sender'],
                    parcel['recipient'],
                    parcel['region_code'],
                    user_id
                ))
            conn.commit()
    finally:
        conn.close()

def get_parcels_for_delivery_by_date(delivery_date, courier_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.* FROM parcels p
                JOIN parcel_invoice pi ON p.parcel_id = pi.parcel_id
                JOIN invoices i ON pi.invoice_id = i.invoice_id
                WHERE i.invoice_type = 'delivery' 
                AND i.planned_delivery_date = %s
                AND i.created_by = %s
                ORDER BY p.internal_number
            """, (delivery_date, courier_id))
            return [{
                'parcel_id': row[0],
                'track_number': row[1],
                'internal_number': row[2],
                'sender': row[3],
                'recipient': row[4],
                'status': row[5],
                'arrival_date': row[6],
                'delivery_date': row[7],
                'region_code': row[9]
            } for row in cursor.fetchall()]
    finally:
        conn.close()

def reschedule_parcel_delivery(parcel_id, new_date, user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE parcels
                SET delivery_date = %s, last_updated_by = %s
                WHERE parcel_id = %s
            """, (new_date, user_id, parcel_id))
            conn.commit()
    finally:
        conn.close()
