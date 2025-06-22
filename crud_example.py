import psycopg2
from psycopg2.extensions import register_type, UNICODE
CONN_STR = "host='10.22.31.252' dbname='rpr24' user='sidorenko_t_v' password='c5c62a89'"

#Просмотр
def print_car():
    register_type(UNICODE)
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute('select * from car')
    result = []
    row = cur.fetchone()
    while row:
        result.append(row)
        row = cur.fetchone()
    cur.close()
    conn.close()
    return result


#Добавление
def add_car(state_num, eng_num, color, brand, tech_passport):
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute('insert into car (state_num, eng_num, color, brand, tech_passport) values\
       (%s, %s, %s, %s, %s)', [state_num, eng_num, color, brand, tech_passport])
    conn.commit()
    cur.close()
    conn.close()


#Обновление
def update_car(state_num, eng_num, color, brand, tech_passport):
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute('UPDATE car SET eng_num = %s, color = %s, brand = %s, tech_passport = %s WHERE state_num = %s', (eng_num, color, brand, tech_passport, state_num))
    conn.commit()

#Удаление
def delete_car(state_num):
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute('DELETE FROM car WHERE state_num = %s', [state_num])
    conn.commit()
    cur.close()
    conn.close()


def get_monthly_inspection_stats(year, month):
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()

    # РџРѕР»СѓС‡Р°РµРј РєРѕР»РёС‡РµСЃС‚РІРѕ РѕСЃРјРѕС‚СЂРѕРІ РїРѕ РґРЅСЏРј
    cur.execute('''
        SELECT 
            DATE_TRUNC('day', date)::date as inspection_date,
            COUNT(*) as vehicles_count
        FROM car_inspection
        WHERE EXTRACT(YEAR FROM date) = %s 
        AND EXTRACT(MONTH FROM date) = %s
        GROUP BY DATE_TRUNC('day', date)
        ORDER BY inspection_date
    ''', (year, month))

    daily_stats = cur.fetchall()

    # РџРѕР»СѓС‡Р°РµРј СЃРїРёСЃРѕРє РёРЅСЃРїРµРєС‚РѕСЂРѕРІ РЅР° Р·Р°РґР°РЅРЅСѓСЋ РґР°С‚Сѓ
    cur.execute('''
        SELECT DISTINCT name
        FROM car_inspection
        WHERE EXTRACT(YEAR FROM date) = %s 
        AND EXTRACT(MONTH FROM date) = %s
    ''', (year, month))

    officers = cur.fetchall()

    # РџРѕР»СѓС‡Р°РµРј РёСЃС‚РѕСЂРёСЋ РѕСЃРјРѕС‚СЂРѕРІ РїРѕ РЅРѕРјРµСЂСѓ РґРІРёРіР°С‚РµР»СЏ
    cur.execute('''
        SELECT DISTINCT c.eng_num
        FROM car_inspection ci
        JOIN car c ON ci.eng_num = c.eng_num
    ''')

    engine_numbers = [row[0] for row in cur.fetchall()]

    conn.close()
    return daily_stats, officers, engine_numbers


def get_officer_inspection_details(date):
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()

    cur.execute('''
        SELECT 
            po.name,
            po.title,
            ci.eng_num,
            ci.result
        FROM car_inspection ci
        JOIN police_officer po ON ci.name = po.name
        WHERE ci.date = %s
    ''', (date,))

    inspections = cur.fetchall()

    conn.close()
    return inspections


def get_vehicle_inspection_history(engine_number):
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()

    cur.execute('''
        SELECT 
            c.eng_num,
            ci.date,
            ci.result
        FROM car_inspection ci
        JOIN car c ON ci.eng_num = c.eng_num
        WHERE c.eng_num = %s
        ORDER BY ci.date
    ''', (engine_number,))

    history = cur.fetchall()

    conn.close()
    return history

class App:
    def run(self):
        choice = 0
        choices = {
            1: print_car,
            2: lambda: add_car(input('Enter state_num: '), input('Enter eng_num: '), input('Enter color: '), input('Enter brand: '), input('Enter tech_passport: ')),
            3: lambda: delete_car(input('Enter state_num to delete: ')),
            4: lambda: update_car(input('Enter state_num to update: '), input('Enter new eng_num: '), input('Enter new color: '), input('Enter new brand: '), input('Enter new tech_passport: ')),
            5: print_owner,
            6: lambda: add_owner(input('Enter licence_num: '), input('Enter name: '), input('Enter address: '), input('Enter birthday (YYYY-MM-DD): '), input('Enter gender: '), input('Enter state_num: ')),
            7: lambda: delete_owner(input('Enter licence_num to delete: ')),
            8: lambda: update_owner(input('Enter current licence_num: '), input('Enter new name: '), input('Enter new address: '), input('Enter new birthday (YYYY-MM-DD): '), input('Enter new gender: '), input('Enter new state_num: ')),
            9: print_officer,
            10: lambda: add_officer(input('Enter name: '), input('Enter position: '), input('Enter title: ')),
            11: lambda: delete_officer(input('Enter name to delete: ')),
            12: lambda: update_officer(input('Enter name: '), input('Enter position: '), input('Enter title: ')),
            13: print_inspection,
            14: lambda: add_inspection(input('Enter date (YYYY-MM-DD): '), input('Enter result: '), input('Enter officer_name: '), input('Enter eng_num: ')),
            15: lambda: delete_inspection(input('Enter officer_name: '), input('Enter date (YYYY-MM-DD): ')),
            16: lambda: update_inspection(input('Enter current date (YYYY-MM-DD): '), input('Enter result: '), input('Enter officer_name: '), input('Enter eng_num: ')),
            18: lambda: add_users(input('Enter login: '), input('Enter password: ')),
            19: lambda: delete_users(input('Enter login to delete: ')),
            20: lambda: update_users(input('Enter login: '), input('Enter new password: '))
        }
        while choice != 21:
            print("\nMenu:")
            print('1. Print car')
            print('2. Add car')
            print('3. Delete car')
            print('4. Update car')
            print('5. Print car owner')
            print('6. Add car owner')
            print('7. Delete car owner')
            print('8. Update car owner')
            print('9. Print police officer')
            print('10. Add police officer')
            print('11. Delete police officer')
            print('12. Update police officer')
            print('13. Print car inspection')
            print('14. Add car inspection')
            print('15. Delete car inspection')
            print('16. Update car inspection')
            print('17. Print users')
            print('18. Add users')
            print('19. Delete users')
            print('20. Update users')
            print('21. EXIT')

            try:
                choice = int(input('Choose an option: '))
                if choice in choices:
                    choices[choice]()
                elif choice != 21:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

if __name__ == '__main__':
    app = App()
    app.run()
