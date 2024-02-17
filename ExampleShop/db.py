import sqlite3
con = sqlite3.connect("bot_db.db")
cur=con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS  user (
    username TEXT (255),
    user_id  INTEGER    PRIMARY KEY
);""")

con.commit()