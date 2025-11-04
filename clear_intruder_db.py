import os
import sqlite3

db_path = 'database/locknest.db'
project_root = os.path.dirname(os.path.abspath(__file__))
static_root = os.path.join(project_root, 'static', 'intruders')

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT id, image_path FROM intruders")
to_delete = []
for row in cur.fetchall():
    id_, image_path = row
    if not image_path:
        to_delete.append(id_)
    else:
        # Only keep the path after "/static/" since static is at project root
        if image_path.startswith("/static/"):
            rel_img_path = image_path[1:]  # remove leading slash
            file_path = os.path.join(project_root, rel_img_path)
        else:
            file_path = os.path.join(static_root, os.path.basename(image_path))
        if not os.path.isfile(file_path):
            to_delete.append(id_)

for id_ in to_delete:
    cur.execute("DELETE FROM intruders WHERE id=?", (id_,))
print(f"Deleted {len(to_delete)} rows with missing images")
conn.commit()
conn.close()
