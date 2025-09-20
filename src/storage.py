import sqlite3
from contextlib import closing

SCHEMA = """
CREATE TABLE IF NOT EXISTS items(
  id TEXT PRIMARY KEY,
  title TEXT,
  url TEXT,
  published_at TEXT,
  source TEXT
);
"""

def get_db(path="data/seen.sqlite"):
  con = sqlite3.connect(path)
  con.execute(SCHEMA)
  return con

def filter_new(con, items):
  new = []
  with closing(con.cursor()) as cur:
    for it in items:
      cur.execute("SELECT 1 FROM items WHERE id=?", (it["id"],))
      if cur.fetchone() is None:
        new.append(it)
  return new

def mark_seen(con, items):
  with con:
    con.executemany(
      "INSERT OR IGNORE INTO items(id,title,url,published_at,source) VALUES(?,?,?,?,?)",
      [(i["id"], i["title"], i["url"], i["published_at"], i["source"]) for i in items]
    )
