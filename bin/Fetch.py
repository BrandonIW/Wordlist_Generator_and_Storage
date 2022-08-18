import sqlite3

conn = sqlite3.connect("E:\Python 3 Training\BootCampUdemy\Projects\Expert - Wordlist Builder\db\password.db")
sql_cursor = conn.cursor()

sql_cursor.execute("SELECT * FROM pass_db")
print(sql_cursor.fetchall())
