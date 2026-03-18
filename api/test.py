import sqlite3
conn = sqlite3.connect("resources.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM resources_fts WHERE resources_fts MATCH ?", ("computer",))
results = cursor.fetchall()
print(len(results[0]))