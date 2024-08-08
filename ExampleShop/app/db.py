import sqlite3 as sq
import json

async def start_db():
    db = sq.connect("bot_db.db")
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS accounts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                card_id INTEGER)""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS items(
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                desc TEXT,
                price TEXT,
                photo TEXT,
                type TEXT
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS card (
                card_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT,
                user_id TEXT,
                count TEXT,
                adress TEXT,
                phone_number TEXT,
                comment TEXT
    )""")
    db.commit()
    db.close()

async def add_id(user_id):
    db = sq.connect("bot_db.db")
    cur = db.cursor()
    user = cur.execute("SELECT * FROM accounts WHERE tg_id == ?", (user_id,)).fetchone()

    if not user:
        cur.execute("INSERT INTO accounts(tg_id) VALUES(?)", (user_id,))
        db.commit()
    db.close()

async def add_item(state):
    db = sq.connect("bot_db.db")
    cur = db.cursor()
    async with state.proxy() as data:
        cur.execute("INSERT INTO items (name,desc,price,photo,type) VALUES (?,?,?,?,?)",
                    (data['name'],
                     data['desc'], 
                     data['price'], 
                     data['photo'], 
                     data['type'])
                    )
        db.commit()
    db.close()

async def find_item(state):
    db = sq.connect("bot_db.db")
    cur = db.cursor() 
    async with state.proxy() as data:
        cur.execute("""SELECT item_id,name,desc,price,photo FROM items WHERE type == ?""", (data['type'],))
        items = cur.fetchall()
    db.close()
    return items


async def add_item_to_card(state, user_id):
    db = sq.connect("bot_db.db")
    cur = db.cursor()
    async with state.proxy() as data:
        item_id = data['item_id']
        count = str(data.get('count', '0'))  # Преобразуем count в строку
        
        # Получить существующие списки item_id и count для пользователя
        cur.execute("SELECT item_id, count FROM card WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        
        if row:
            items_json, counts_json = row
            items_list = json.loads(items_json) if items_json else []
            counts_list = json.loads(counts_json) if counts_json else []
        else:
            items_list = []
            counts_list = []
        
        # Проверить, есть ли уже такой item_id в списке
        if item_id in items_list:
            index = items_list.index(item_id)
            counts_list[index] = str(int(counts_list[index]) + int(count))  # Обновляем количество
        else:
            items_list.append(item_id)
            counts_list.append(count)  # Добавляем новое количество
        
        # Преобразуем обновленные списки обратно в JSON строки
        items_json = json.dumps(items_list)
        counts_json = json.dumps(counts_list)
        
        # Обновить или вставить запись в таблицу card
        if row:
            cur.execute("""UPDATE card 
                           SET item_id = ?, count = ?
                           WHERE user_id = ?""",
                        (items_json, counts_json, user_id))
        else:
            cur.execute("""INSERT INTO card (user_id, items_id, count) 
                           VALUES (?, ?, ?)""",
                        (user_id, items_json, counts_json))
        
        db.commit()
    db.close()


async def show_card(user_id):
    db = sq.connect("bot_db.db")
    cur = db.cursor()
    cur.execute("""SELECT item_id, count FROM card WHERE user_id = ?""", (user_id,))
    row = cur.fetchone()
    
    if row:
        items_json, counts_json = row
        items_list = json.loads(items_json) if items_json else []
        counts_list = json.loads(counts_json) if counts_json else []
    else:
        items_list = []
        counts_list = []
    
    db.close()
    
    # Вернуть списки item_id и count
    return items_list, counts_list

async def get_item_details(item_id):
    db = sq.connect("bot_db.db")
    cur = db.cursor()
    cur.execute("""SELECT name, desc, price, photo FROM items WHERE item_id = ?""", (item_id,))
    item = cur.fetchone()
    db.close()
    return item


async def update_item_count(user_id, item_id, increase=True):
    db = sq.connect("bot_db.db")
    cur = db.cursor()
    
    try:
        # Получить существующие данные корзины
        cur.execute("SELECT item_id, count FROM card WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        
        if row:
            item_ids_json, counts_json = row
            print("Original item_ids_json:", item_ids_json)
            print("Original counts_json:", counts_json)
            
            # Проверка и обработка данных
            item_ids_list = json.loads(item_ids_json) if item_ids_json else []
            counts_list = json.loads(counts_json) if counts_json else []
            
            print("Decoded item_ids_list:", item_ids_list)
            print("Decoded counts_list:", counts_list)

            # Преобразование item_id к строке для сравнения
            item_id_str = str(item_id)
            print("Item ID as string:", item_id_str)

            if item_id_str in item_ids_list:
                index = item_ids_list.index(item_id_str)
                print("Item index found:", index)
                
                # Преобразование count к целому числу для арифметики
                counts_list = list(map(int, counts_list))
                
                if increase:
                    counts_list[index] += 1
                else:
                    if counts_list[index] > 1:
                        counts_list[index] -= 1
                    else:
                        # Если количество становится 0, удалить товар из корзины
                        item_ids_list.pop(index)
                        counts_list.pop(index)
                
                # Преобразовать обновленные списки в строки JSON
                item_ids_json = json.dumps(item_ids_list)
                counts_json = json.dumps(counts_list)

                print("Updated item_ids_json:", item_ids_json)
                print("Updated counts_json:", counts_json)

                # Обновить запись в базе данных
                cur.execute("""UPDATE card SET item_id = ?, count = ? WHERE user_id = ?""",
                            (item_ids_json, counts_json, user_id))
            else:
                print(f"Item ID {item_id_str} not found in user's cart.")
        else:
            print(f"No cart found for user_id {user_id}.")
        
        db.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()






async def add_order_info(state):
    db = sq.connect("bot_db.db")
    cur = db.cursor() 
    async with state.proxy() as data:
        cur.execute("""INSERST INTO card (adress,phone_number,comment) VALUES(?,?,?)""",(
            data['adress'],
            data['phone_number'],
            data['comment']
        ))
        db.commit()
    db.close()