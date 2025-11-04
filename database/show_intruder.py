import sqlite3

con = sqlite3.connect('locknest.db')
cur = con.cursor()
for row in cur.execute('SELECT image_path FROM intruders'):
    print(row)
con.close()
