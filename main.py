from ctypes import CDLL
from tkinter import *
from tkinter import _cnfmerge
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import font
import sqlite3
import json
import time
import math
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
    global playing
    main.pack(expand=True, fill="both")
    playing = False

def login_page():
    loginp.pack(expand=True, fill="both")

def signup_page():
    signupp.pack(expand=True, fill="both")

def game_page():
    global playing
    game.pack(expand=True, fill="both")
    playing = True

def relative_to_absolute(rel_x, rel_y):
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w/h > ratio:
        draw_w = h * ratio
        draw_h = h
        offset_x = (w - draw_w) / 2
        offset_y = 0
    else:
        draw_w = w
        draw_h = w / ratio
        offset_x = 0
        offset_y = (h - draw_h) / 2
    abs_x = round(offset_x + (rel_x / rel_width) * draw_w)
    abs_y = round(offset_y + (rel_y / rel_height) * draw_h)
    return abs_x, abs_y

def absolute_to_relative(abs_x, abs_y):
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w/h > ratio:
        draw_w = h * ratio
        draw_h = h
        offset_x = (w - draw_w) / 2
        offset_y = 0
    else:
        draw_w = w
        draw_h = w / ratio
        offset_x = 0
        offset_y = (h - draw_h) / 2
    rel_x = round((abs_x - offset_x) / draw_w * rel_width)
    rel_y = round((abs_y - offset_y) / draw_h * rel_height)
    return rel_x, rel_y

def offset_info():
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w/h > ratio:
        draw_w = h * ratio
        offset_x = round((w - draw_w) / 2)
        xloffset = (0, offset_x)
        xroffset = (math.ceil(w) - offset_x - offset_x + xloffset[1], math.ceil(w))
        x_offset_info = (xloffset, xroffset)
        y_offset_info = ((0, 0), (math.ceil(h), math.ceil(h)))
    else:
        draw_h = w / ratio
        offset_y = round((h - draw_h) / 2)
        ynoffset = (0, offset_y)
        ysoffset = (math.ceil(h) - offset_y - offset_y + ynoffset[1], math.ceil(h))
        x_offset_info = ((0, 0), (math.ceil(w), math.ceil(w)))
        y_offset_info = (ynoffset, ysoffset)
    _offset_info = (x_offset_info, y_offset_info)
    return _offset_info

def crop_img(canvas, image_path, x1, y1, x2, y2):
    img = Image.open(image_path)
    target_width = x2 - x1
    target_height = y2 - y1
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height
    if img_ratio > target_ratio:
        new_height = target_height
        new_width = round(target_height * img_ratio)
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        offset_x = (new_width - target_width) // 2
        offset_y = 0
        img_cropped = img_resized.crop((offset_x, 0, offset_x + target_width, target_height))
    else:
        new_width = target_width
        new_height = round(target_width / img_ratio)
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        offset_x = 0
        offset_y = (new_height - target_height) // 2
        img_cropped = img_resized.crop((0, offset_y, target_width, offset_y + target_height))
    tk_img = ImageTk.PhotoImage(img_cropped)
    return tk_img

def quit():
    global running
    running = False

cols = """id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL UNIQUE,
password TEXT NOT NULL,
score INTEGER DEFAULT 0"""

window_size = "1440x960+-8+0"
ratio = 1440 / 960
rel_width = 960
rel_height = rel_width / ratio

special = ["WORDS", "ORDER", "INPUT", "VOCAB", "LOGIC", "LINKS", "CHAIN", "MERGE", "GAMES", "CLAIM"]

title = "Word Game"

score = 0
maxscore = 0

running = True
playing = False

with open("./data/words.json", "r") as f:
    words = json.load(f)

root = Tk()
root.title(title)
root.geometry(window_size)
root.protocol("WM_DELETE_WINDOW", quit)

arrow = ImageTk.PhotoImage(Image.open("img/arrow.png").resize((30, 30), Image.LANCZOS))

main = TkPageFrame(root)
inf = Frame(main)
inf.place(relx=1.0, rely=0.0, anchor="ne")
login = Button(inf, text="Log In", font=font.Font(size=20), command=login_page, cursor="hand2")
login.pack(side="right")
signup = Button(inf, text="Sign Up", font=font.Font(size=20), command=signup_page, cursor="hand2")
signup.pack(side="left")
title_lbl = Label(main, text=title, font=font.Font(size=40))
title_lbl.place(relx=0.5, rely=0.2, anchor="n")
start = Button(main, text="Start", font=font.Font(size=20), padx=40, pady=20, command=game_page, cursor="hand2")
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
lsubmit = Button(lss, text="Submit", font=font.Font(size=20), cursor="hand2")
lsubmit.pack(side="left")
signupl = Button(lss, text="Sign Up", command=signup_page, font=font.Font(size=20), cursor="hand2")
signupl.pack(side="right")
lback = Button(loginp, image=arrow, command=main_page, borderwidth=0, highlightthickness=0, bd=0, relief="flat", cursor="hand2")
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
ssubmit = Button(sss, text="Submit", font=font.Font(size=20), cursor="hand2")
ssubmit.pack(side="left")
logins = Button(sss, text="Log In", command=login_page, font=font.Font(size=20), cursor="hand2")
logins.pack(side="right")
sback = Button(signupp, image=arrow, command=main_page, borderwidth=0, highlightthickness=0, bd=0, relief="flat", cursor="hand2")
sback.place(relx=0.01, rely=0.01, anchor="nw")

game = TkPageFrame(root)
canvas = Canvas(game)
canvas.pack(expand=True, fill="both")
lbl_txt = Label(game, text="Letters: ", font=font.Font(size=20))
lbl_txt.pack(fill="y", pady=10)
main.pack(expand=True, fill="both")

magnet = (rel_width // 2 - 50, rel_height - 100, rel_width // 2 + 50, rel_height)

while running:
    if playing:
        canvas.delete("all")
        offset = offset_info()
        print(offset[0][0][1], offset[1][0][1], offset[0][1][0], offset[1][1][0])
        print(canvas.winfo_width(), canvas.winfo_height())
        bg_img = crop_img(canvas, "img/background.png", offset[0][0][1], offset[1][0][1], offset[0][1][0], offset[1][1][0])
        canvas.create_image(offset[0][0][1], offset[1][0][1], anchor='nw', image=bg_img)
        magnet_abs = (*relative_to_absolute(magnet[0], magnet[1]), *relative_to_absolute(magnet[2], magnet[3]))
        magnet_img = crop_img(canvas, "img/magnet.png", *magnet_abs)
        canvas.create_image(magnet_abs[0], magnet_abs[1], anchor='nw', image=magnet_img)
    root.update()
    time.sleep(0.01626)