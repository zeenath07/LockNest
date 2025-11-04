import sqlite3
con = sqlite3.connect('locknest.db')
cur = con.cursor()
cur.execute('DELETE FROM intruders')
con.commit()
con.close()
print("All intruder records deleted")
