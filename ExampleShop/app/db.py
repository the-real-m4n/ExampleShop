import sqlite3 as sq

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

async def add_item_to_card(state,user_id):
    db = sq.connect("bot_db.db")
    cur = db.cursor() 
    async with state.proxy() as data:
        count=str(data.get('count','0'))
        cur.execute("""INSERT INTO card (user_id,item_id,count) VALUES (?,?,?) """,
                   (user_id,
                    data['item_id'],
                    count,)
                     )
        db.commit()
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