from ctypes import CDLL
from tkinter import *
from tkinter import _cnfmerge
from PIL import Image, ImageTk
from tkinter import font
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

class TkPageFrame(Widget):
    def __init__(self, master=None, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        cnf = _cnfmerge((cnf, kw))
        extra = ()
        if "class_" in cnf:
            extra = ("-class", cnf["class_"])
            del cnf["class_"]
        elif "class" in cnf:
            extra = ("-class", cnf["class"])
            del cnf["class"]
        if "name" in cnf:
            del cnf["name"]
        Widget.__init__(self, master, "frame", cnf, {}, extra)

    def _forget_siblings(self):
        for k, w in self.master.children.items():
            if k.startswith("!tkpageframe"):
                w.pack_forget()
                w.grid_forget()
                w.place_forget()

    def pack(self, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        self._forget_siblings()
        super().pack_configure(cnf, **kw)

    def grid(self, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        self._forget_siblings()
        super().grid_configure(cnf, **kw)

    def place(self, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        self._forget_siblings()
        super().place_configure(cnf, **kw)

def main_page():
    main.pack(expand=True, fill="both")

def login_page():
    loginp.pack(expand=True, fill="both")

def signup_page():
    signupp.pack(expand=True, fill="both")

cols = """id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL UNIQUE,
password TEXT NOT NULL,
score INTEGER DEFAULT 0"""

window_size = "1440x960+-8+0"

special = ["WORDS", "ORDER", "INPUT", "VOCAB", "LOGIC", "LINKS", "CHAIN", "MERGE", "GAMES", "CLAIM"]

title = "Word Game"

score = 0
maxscore = 0

with open("./data/words.json", "r") as f:
    words = json.load(f)

root = Tk()
root.title(title)
root.geometry(window_size)

arrow = ImageTk.PhotoImage(Image.open("img/arrow.png").resize((30, 30), Image.LANCZOS))

main = TkPageFrame(root)
inf = Frame(main)
inf.place(relx=1.0, rely=0.0, anchor="ne")
login = Button(inf, text="Log In", font=font.Font(size=20), command=login_page)
login.pack(side="right")
signup = Button(inf, text="Sign Up", font=font.Font(size=20), command=signup_page)
signup.pack(side="left")
title_lbl = Label(main, text=title, font=font.Font(size=40))
title_lbl.place(relx=0.5, rely=0.2, anchor="n")
start = Button(main, text="Start", font=font.Font(size=20), padx=40, pady=20)
start.place(relx=0.5, rely=0.5, anchor="n")
score_fr = Frame(main)
score_fr.place(relx=0.5, rely=0.7, anchor="n", relwidth=0.3)
score_lbl = Label(score_fr, text=("Score: " + str(score)), font=font.Font(size=20))
score_lbl.pack(side="left", anchor="w")
max_score_lbl = Label(score_fr, text=("High Score: " + str(maxscore)), font=font.Font(size=20))
max_score_lbl.pack(side="right", anchor="e")

loginp = TkPageFrame(root)
ltitle_lbl = Label(loginp, text="Log In", font=font.Font(size=30))
ltitle_lbl.place(relx=0.5, rely=0.25, anchor="n")
login_form = Frame(loginp)
login_form.place(relx=0.5, rely=0.35, anchor="n")
username_login = Frame(login_form)
username_login.pack(anchor="e")
lun_lbl = Label(username_login, text="Username  ", font=font.Font(size=20))
lun_lbl.pack(side="left")
lun_ent = Entry(username_login, font=font.Font(size=20))
lun_ent.pack(side="right")
password_login = Frame(login_form)
password_login.pack(anchor="e")
lpw_lbl = Label(password_login, text="Password  ", font=font.Font(size=20))
lpw_lbl.pack(side="left")
lpw_ent = Entry(password_login, font=font.Font(size=20), show="·")
lpw_ent.pack(side="right")
lss = Frame(loginp)
lss.place(relx=0.5, rely=0.45, anchor="n")
lsubmit = Button(lss, text="Submit", font=font.Font(size=20))
lsubmit.pack(side="left")
signupl = Button(lss, text="Sign Up", command=signup_page, font=font.Font(size=20))
signupl.pack(side="right")
lback = Button(loginp, image=arrow, command=main_page, borderwidth=0, highlightthickness=0, bd=0, relief="flat")
lback.place(relx=0.01, rely=0.01, anchor="nw")

signupp = TkPageFrame(root)
stitle_lbl = Label(signupp, text="Sign Up", font=font.Font(size=30))
stitle_lbl.place(relx=0.5, rely=0.25, anchor="n")
signup_form = Frame(signupp)
signup_form.place(relx=0.5, rely=0.35, anchor="n")
username_signup = Frame(signup_form)
username_signup.pack(anchor="e")
sun_lbl = Label(username_signup, text="Username  ", font=font.Font(size=20))
sun_lbl.pack(side="left")
sun_ent = Entry(username_signup, font=font.Font(size=20))
sun_ent.pack(side="right")
password_signup = Frame(signup_form)
password_signup.pack(anchor="e")
spw_lbl = Label(password_signup, text="Password  ", font=font.Font(size=20))
spw_lbl.pack(side="left")
spw_ent = Entry(password_signup, font=font.Font(size=20), show="·")
spw_ent.pack(side="right")
passwordconfirm_signup = Frame(signup_form)
passwordconfirm_signup.pack(anchor="e")
spc_lbl = Label(passwordconfirm_signup, text="Password Confirm  ", font=font.Font(size=20))
spc_lbl.pack(side="left")
spc_ent = Entry(passwordconfirm_signup, font=font.Font(size=20), show="·")
spc_ent.pack(side="right")
sss = Frame(signupp)
sss.place(relx=0.5, rely=0.485, anchor="n")
ssubmit = Button(sss, text="Submit", font=font.Font(size=20))
ssubmit.pack(side="left")
logins = Button(sss, text="Log In", command=login_page, font=font.Font(size=20))
logins.pack(side="right")
sback = Button(signupp, image=arrow, command=main_page, borderwidth=0, highlightthickness=0, bd=0, relief="flat")
sback.place(relx=0.01, rely=0.01, anchor="nw")

main.pack(expand=True, fill="both")

root.mainloop()