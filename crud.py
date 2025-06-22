import psycopg2
from psycopg2.extensions import register_type, UNICODE

# Подключение к БД
def get_db_connection():
    """Универсальная функция для подключения к PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="your_host",
            dbname="your_dbname",
            user="your_username",
            password="your_password"
        )
        register_type(UNICODE)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

# CRUD операции (универсальные шаблоны)
def search_records(table_name, conditions=None, columns="*"):
    """
    Поиск записей в таблице
    :param table_name: имя таблицы
    :param conditions: словарь условий {поле: значение}
    :param columns: список полей для выборки (по умолчанию все)
    :return: список найденных записей
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        # Формируем SQL запрос
        query = f"SELECT {columns} FROM {table_name}"
        params = []
        
        if conditions:
            query += " WHERE " + " AND ".join([f"{k} = %s" for k in conditions.keys()])
            params = list(conditions.values())
        
        cur.execute(query, params)
        records = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]
        
        return [dict(zip(col_names, record)) for record in records]
    except Exception as e:
        print(f"Ошибка при поиске записей: {e}")
        return []
    finally:
        if conn:
            conn.close()

def add_record(table_name, data):
    """
    Добавление записи в таблицу
    :param table_name: имя таблицы
    :param data: словарь {поле: значение}
    :return: ID добавленной записи или None
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders}) RETURNING id"
        
        cur.execute(query, list(data.values()))
        record_id = cur.fetchone()[0]
        conn.commit()
        
        return record_id
    except Exception as e:
        print(f"Ошибка при добавлении записи: {e}")
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def update_record(table_name, record_id, data):
    """
    Обновление записи в таблице
    :param table_name: имя таблицы
    :param record_id: ID обновляемой записи
    :param data: словарь {поле: новое значение}
    :return: количество обновленных записей
    """
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cur = conn.cursor()
        
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        
        cur.execute(query, list(data.values()) + [record_id])
        conn.commit()
        
        return cur.rowcount
    except Exception as e:
        print(f"Ошибка при обновлении записи: {e}")
        conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()

def delete_record(table_name, record_id):
    """
    Удаление записи из таблицы
    :param table_name: имя таблицы
    :param record_id: ID удаляемой записи
    :return: количество удаленных записей
    """
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cur = conn.cursor()
        query = f"DELETE FROM {table_name} WHERE id = %s"
        cur.execute(query, (record_id,))
        conn.commit()
        return cur.rowcount
    except Exception as e:
        print(f"Ошибка при удалении записи: {e}")
        conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()

#?
# Импорт данных из файлов
def import_from_csv(table_name, file_path, delimiter=","):
    """
    Импорт данных из CSV в таблицу
    :param table_name: имя таблицы
    :param file_path: путь к CSV файлу
    :param delimiter: разделитель (по умолчанию запятая)
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Пропускаем заголовок
            headers = f.readline().strip().split(delimiter)
            placeholders = ", ".join(["%s"] * len(headers))
            
            for line in f:
                values = line.strip().split(delimiter)
                query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
                cur.execute(query, values)
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка при импорте из CSV: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def import_from_json(table_name, file_path):
    """
    Импорт данных из JSON в таблицу
    :param table_name: имя таблицы
    :param file_path: путь к JSON файлу
    """
    import json
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                headers = list(data[0].keys())
                placeholders = ", ".join(["%s"] * len(headers))
                
                for item in data:
                    values = [item.get(key) for key in headers]
                    query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
                    cur.execute(query, values)
                
                conn.commit()
                return True
            return False
    except Exception as e:
        print(f"Ошибка при импорте из JSON: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
