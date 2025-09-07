from ctypes import CDLL
from tkinter import *
import sqlite3
import json
import os

class DBManager:
    def __init__(self, file, auto_commit=False):
        self.file = file
        if auto_commit:
            self.conn = sqlite3.connect(self.file, isolation_level=None)
        else:
            self.conn = sqlite3.connect(self.file)
        self.c = self.conn.cursor()
    def process(self, query, /, table=None, *, col=None, con=None, con_params=(), **kw):
        if query == "create":
            if not col:
                raise ValueError("Column definition is required for create.")
            self.c.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col})")
        elif query == "exist":
            self.c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table, ))
            return self.c.fetchone() is not None
        elif query == "drop":
            self.c.execute(f"DROP TABLE IF EXISTS {table}")
        elif query == "insert":
            cols = ", ".join(kw.keys())
            placeholders = ", ".join("?" for _ in kw.keys())
            values = tuple(kw.values())
            self.c.execute(f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})", values)
        elif query == "update":
            set_clause = ", ".join(f"{col_}=?" for col_ in kw.keys())
            values = tuple(kw.values())
            where_clause = f"WHERE {con}" if con else ""
            self.c.execute(f"UPDATE OR IGNORE {table} SET {set_clause} {where_clause}", values + con_params)
        elif query == "select":
            where_clause = f"WHERE {con}" if con else ""
            self.c.execute(f"SELECT * FROM {table} {where_clause}", con_params)
            return self.c.fetchall()
        elif query == "delete":
            where_clause = f"WHERE {con}" if con else ""
            self.c.execute(f"DELETE FROM {table} {where_clause}", con_params)
        elif query == "rollback":
            self.conn.rollback()
        elif query == "commit":
            self.conn.commit()
        elif query == "close":
            self.conn.commit()
            self.conn.close()

class TkPageFrame(Frame):
    def __init__(self, master=None, cnf={}, **kw):
        kw["name"] = "tkpageframe"
        super().__init__(master, cnf, **kw)

cols = """id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL UNIQUE,
password TEXT NOT NULL,
score INTEGER DEFAULT 0"""

game_size = "1440x960"

with open("./data/words.json", "r") as f:
    words = json.load(f)