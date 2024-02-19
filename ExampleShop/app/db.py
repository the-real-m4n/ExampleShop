import sqlite3 as sq

async def start_db():
    db = sq.connect("bot_db.db")
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS accounts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                card_id TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS items(
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                desc TEXT,
                price TEXT,
                photo TEXT,
                type TEXT
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