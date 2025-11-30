from tkinter import *
from tkinter import _cnfmerge
from tkinter import messagebox
from PIL import Image, ImageTk
from collections import Counter
from dotenv import load_dotenv
from tkinter import font
import keyboard
import requests
import process
import sqlite3
import hashlib
import atexit
import random
import base64
import json
import time
import math
import sys
import os

class DBManager:
    def __init__(self, file, connected=False, auto_commit=False):
        if connected:
            self.file = None
            self.conn = file
        else:
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

def main_page(win=False):
    global playing, state
    state = "main"
    main.pack(expand=True, fill="both")
    playing = False
    score_lbl.configure(text=("Score: " + str(score)))
    max_score_lbl.configure(text=("High Score: " + str(maxscore)))
    if win:
        if hard:
            win_lbl.configure(text="HARD MODE CLEAR!")
        else:
            win_lbl.configure(text="YOU WIN!")
    else:
        win_lbl.configure(text="")

def login_page():
    global state
    state = "login"
    loginp.pack(expand=True, fill="both")
    lun_ent.delete(0, "end")
    lpw_ent.delete(0, "end")
    lun_ent.focus_set()

def signup_page():
    global state
    state = "signup"
    signupp.pack(expand=True, fill="both")
    sun_ent.delete(0, "end")
    spw_ent.delete(0, "end")
    spc_ent.delete(0, "end")

def game_page():
    global playing, state, hard
    state = "game"
    hard = True
    game.pack(expand=True, fill="both")
    playing = True
    reset()

def mypage_page():
    global state
    state = "mypage"
    mypage.pack(expand=True, fill="both")
    id_lbl.configure(text=login_data[1])
    mscore.configure(text=f"High Score: {max(login_data[3], maxscore)}")

def chpw_page():
    global state
    state = "change_password"
    chpw.pack(expand=True, fill="both")
    pwc_ent.delete(0, "end")
    npw_ent.delete(0, "end")
    npc_ent.delete(0, "end")

def delid_page():
    global state
    state = "delete_id"
    delid.pack(expand=True, fill="both")
    dun_ent.delete(0, "end")
    dpw_ent.delete(0, "end")

def relative_to_absolute(rel_x, rel_y):
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w / h > ratio:
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
    if w / h > ratio:
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
    if w / h > ratio:
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

def crop_img(image_path, x1, y1, x2, y2):
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

def encode_str(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def login_process(username, password, state):
    global login_data, maxscore
    processed = db.process("select", "user", con="username = ?", con_params=(username, ))
    if len(processed) > 1:
        raise ValueError
    if len(processed) == 0:
        if state == "signup":
            raise ValueError
        messagebox.showerror("Incorrect Username", "Incorrect Username")
        lun_ent.delete(0, "end")
        lun_ent.focus_set()
        return
    if processed[0][2] != encode_str(password):
        if state == "signup":
            raise ValueError
        messagebox.showerror("Incorrect Password", "Incorrect Password")
        lpw_ent.delete(0, "end")
        lpw_ent.focus_set()
        return
    login_data = processed[0]
    maxscore = max(processed[0][3], maxscore)
    login.configure(text="Log Out", command=logout)
    signup.configure(text="My Page", command=mypage_page)
    main_page()

def logout():
    global login_data
    db.process("update", "user", con="username = ?", con_params=(login_data[1], ), score=maxscore)
    login_data = None
    login.configure(text="Log In", command=login_page)
    signup.configure(text="Sign Up", command=signup_page)

def chpw_submit():
    global login_data
    if login_data[2] != encode_str(pwc_ent.get()):
        messagebox.showerror("Incorrect Password", "Incorrect Password")
        pwc_ent.delete(0, "end")
        return
    if npw_ent.get() != npc_ent.get():
        messagebox.showerror("Password Different", "Password Different")
        npw_ent.delete(0, "end")
        npc_ent.delete(0, "end")
        return
    encoded = encode_str(npw_ent.get())
    db.process("update", "user", con="username = ?", con_params=(login_data[1], ), password=encoded)
    login_data = (login_data[0], login_data[1], encoded, login_data[3])
    mypage_page()

def delid_submit():
    global login_data
    username = dun_ent.get()
    password = dpw_ent.get()
    if login_data[1] != username:
        messagebox.showerror("Incorrect Username", "Incorrect Username")
        dun_ent.delete(0, "end")
        return
    if login_data[2] != encode_str(password):
        messagebox.showerror("Incorrect Password", "Incorrect Password")
        dpw_ent.delete(0, "end")
        return
    if not messagebox.askyesno("Delete Account", "Are you sure to delete the account? This action cannot be undone.", default="no"):
        mypage_page()
        return
    db.process("delete", "user", con="username = ?", con_params=(login_data[1], ))
    login_data = None
    login.configure(text="Log In", command=login_page)
    signup.configure(text="Sign Up", command=signup_page)
    main_page()

def login_submit():
    username = lun_ent.get()
    password = lpw_ent.get()
    login_process(username, password, "login")

def signup_submit():
    username = sun_ent.get()
    password = spw_ent.get()
    passconf = spc_ent.get()
    processed = db.process("select", "user", con="username = ?", con_params=(username, ))
    if len(processed) > 1:
        raise ValueError
    if len(processed) == 1 or username == "":
        messagebox.showerror("Invalid Username", "Invalid Username")
        sun_ent.delete(0, "end")
        return
    if password == "":
        messagebox.showerror("Invalid Password", "Invalid Password")
        spw_ent.delete(0, "end")
        spc_ent.delete(0, "end")
        return
    if password != passconf:
        messagebox.showerror("Password Different", "Password Different")
        spw_ent.delete(0, "end")
        spc_ent.delete(0, "end")
        return
    db.process("insert", "user", username=username, password=encode_str(password))
    login_process(username, password, "signup")

@atexit.register
def quit():
    global running, _exit
    if _exit:
        return
    _exit = True
    if not messagebox.askokcancel("Quit Game", "Are you sure to quit the game?", default="cancel"):
        return
    if login_data:
        logout()
    running = False
    if github_data["token"]:
        db.process("commit")
        data_txt = db.conn.serialize()
        db.process("close")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_data["token"]}"
        }
        url = f"https://api.github.com/repos/{github_data["owner"]}/{github_data["repo"]}/contents/{github_data["path"]}"
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        sha = res.json()["sha"]
        data_b64 = base64.b64encode(data_txt).decode()
        data_send = {
            "message": "update file database.db via GitHub API",
            "content": data_b64,
            "sha": sha
        }
        res = requests.put(url, json=data_send, headers=headers)
        res.raise_for_status()

def esc():
    match state:
        case "main":
            quit()
        case "login" | "signup" | "mypage" | "game":
            main_page()
        case "change_password" | "delete_id":
            mypage_page()

def reset():
    global magnet, magnet_v, letter_cnt, letter0x, letter, letter_v, letters, atch, atcf, bomb_cnt, bomb0x, bomb, bomb_v, mode, magdmx, letter_a, score, word_n
    magnet0 = (rel_width // 2 - 25, int(rel_height) - 51, rel_width // 2 + 25, int(rel_height) - 1)
    magnet = magnet0
    magnet_v = [0, 0]
    letter_cnt = 0
    letter0x = []
    letter = []
    letter_v = []
    letters = []
    atch = []
    atcf = []
    bomb_cnt = 0
    bomb0x = []
    bomb = []
    bomb_v = []
    mode = "0"
    magdmx = 200
    letter_a = 1
    score = 0
    word_n = ""

if getattr(sys, "frozen", False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)

_exit = False

cols = """id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL UNIQUE,
password TEXT NOT NULL,
score INTEGER DEFAULT 0"""

resp = requests.get("https://github.com/seanleeee13/text-magnet-db/raw/refs/heads/main/database.db")
resp.raise_for_status()

dbf = sqlite3.connect(":memory:", isolation_level=None)
dbf.deserialize(resp.content)
db = DBManager(dbf, connected=True)
db.process("create", "user", col=cols)

load_dotenv()

github_data = {
    "owner": "seanleeee13",
    "repo": "text-magnet-db",
    "path": "database.db",
    "token": os.getenv("GITHUB_TOKEN")
}

window_size = "1440x930+-8+0"
ratio = 1440 / 960
rel_width = 960
rel_height = rel_width / ratio
last_win_size = (0, 0)

title = "Word Game"

score = 0
maxscore = 0
login_data = None

with open(os.path.join(base_path, "data", "words.json"), "r") as f:
    words = json.load(f)
special = ["ORDER", "INPUT", "VOCAB", "LOGIC", "LINKS", "CHAIN", "MERGE", "GAMES", "CLAIM", "WORDS"]
mostsp = "WORDS"
letter_list = list(Counter("".join(words)).elements())
special_letter_list = sum(list(map(list, special + [mostsp] * 10)), start=[]) * 100
letter_list += special_letter_list

root = Tk()
root.title(title)
root.geometry(window_size)
root.minsize(525, 350)
root.protocol("WM_DELETE_WINDOW", quit)
root.state("zoomed")
root.bind("<Escape>", lambda _: esc())

arrow = ImageTk.PhotoImage(Image.open(os.path.join(base_path, "img", "arrow.png")).resize((30, 30), Image.LANCZOS))

state = "main"
running = True
playing = False

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
max_score_lbl.pack(side="right", anchor="center")
win_lbl = Label(main, text="", font=font.Font(size=20))
win_lbl.place(relx=0.5, rely=0.8, anchor="n")

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
lsubmit = Button(loginp, text="Log In", font=font.Font(size=20), cursor="hand2", command=login_submit)
lsubmit.place(relx=0.5, rely=0.45, anchor="n")
signupllblfr = Frame(loginp)
signupllblfr.place(relx=0.5, rely=0.55, anchor="n")
signupllbl = Label(signupllblfr, text="Have no account?", font=font.Font(size=15))
signupllbl.pack(side="left")
signupllbn = Label(signupllblfr, text="Sign Up", font=font.Font(size=15), cursor="hand2", foreground="blue")
signupllbn.pack(side="right")
lback = Button(loginp, image=arrow, command=main_page, borderwidth=0, highlightthickness=0, bd=0, relief="flat", cursor="hand2")
lback.place(relx=0.01, rely=0.01, anchor="nw")
lun_ent.bind("<Return>", lambda _: lpw_ent.focus_set() if not lpw_ent.get() else login_submit())
lpw_ent.bind("<Return>", lambda _: lun_ent.focus_set() if not lun_ent.get() else login_submit())
signupllbn.bind("<ButtonRelease-1>", lambda _: signup_page())

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
ssubmit = Button(signupp, text="Sign Up", font=font.Font(size=20), cursor="hand2", command=signup_submit)
ssubmit.place(relx=0.5, rely=0.485, anchor="n")
loginslblfr = Frame(signupp)
loginslblfr.place(relx=0.5, rely=0.585, anchor="n")
loginslbl = Label(loginslblfr, text="Have account?", font=font.Font(size=15))
loginslbl.pack(side="left")
loginslbn = Label(loginslblfr, text="Log in", font=font.Font(size=15), cursor="hand2", foreground="blue")
loginslbn.pack(side="right")
sback = Button(signupp, image=arrow, command=main_page, borderwidth=0, highlightthickness=0, bd=0, relief="flat", cursor="hand2")
sback.place(relx=0.01, rely=0.01, anchor="nw")
sun_ent.bind("<Return>", lambda _: spw_ent.focus_set() if not spw_ent.get() else spc_ent.focus_set() if not spc_ent.get() else signup_submit())
spw_ent.bind("<Return>", lambda _: sun_ent.focus_set() if not sun_ent.get() else spc_ent.focus_set() if not spc_ent.get() else signup_submit())
spc_ent.bind("<Return>", lambda _: sun_ent.focus_set() if not sun_ent.get() else spw_ent.focus_set() if not spw_ent.get() else signup_submit())
loginslbn.bind("<ButtonRelease-1>", lambda _: login_page())

mypage = TkPageFrame(root)
id_lbl = Label(mypage, font=font.Font(size=30))
id_lbl.place(relx=0.5, rely=0.25, anchor="n")
mscore = Label(mypage, font=font.Font(size=20))
mscore.place(relx=0.5, rely=0.4, anchor="n")
mbtnfr = Frame(mypage)
mbtnfr.place(relx=0.5, rely=0.5, anchor="n")
chpswd = Button(mbtnfr, text="Change Password", font=font.Font(size=15), cursor="hand2", command=chpw_page)
chpswd.pack(side="left")
dlacnt = Button(mbtnfr, text="Delete Account", font=font.Font(size=15), cursor="hand2", command=delid_page)
dlacnt.pack(side="right")
mback = Button(mypage, image=arrow, command=main_page, borderwidth=0, highlightthickness=0, bd=0, relief="flat", cursor="hand2")
mback.place(relx=0.01, rely=0.01, anchor="nw")

chpw = TkPageFrame(root)
ctitle_lbl = Label(chpw, text="Change Password", font=font.Font(size=30))
ctitle_lbl.place(relx=0.5, rely=0.25, anchor="n")
chpw_form = Frame(chpw)
chpw_form.place(relx=0.5, rely=0.35, anchor="n")
pw_chpw = Frame(chpw_form)
pw_chpw.pack(anchor="e")
pwc_lbl = Label(pw_chpw, text="Password  ", font=font.Font(size=20))
pwc_lbl.pack(side="left")
pwc_ent = Entry(pw_chpw, font=font.Font(size=20), show="·")
pwc_ent.pack(side="right")
npw_chpw = Frame(chpw_form)
npw_chpw.pack(anchor="e")
npw_lbl = Label(npw_chpw, text="New Password  ", font=font.Font(size=20))
npw_lbl.pack(side="left")
npw_ent = Entry(npw_chpw, font=font.Font(size=20), show="·")
npw_ent.pack(side="right")
npc_chpw = Frame(chpw_form)
npc_chpw.pack(anchor="e")
npc_lbl = Label(npc_chpw, text="Password Confirm  ", font=font.Font(size=20))
npc_lbl.pack(side="left")
npc_ent = Entry(npc_chpw, font=font.Font(size=20), show="·")
npc_ent.pack(side="right")
csubmit = Button(chpw, text="Submit", font=font.Font(size=20), cursor="hand2", command=chpw_submit)
csubmit.place(relx=0.5, rely=0.485, anchor="n")
cback = Button(chpw, image=arrow, command=mypage_page, borderwidth=0, highlightthickness=0, bd=0, relief="flat", cursor="hand2")
cback.place(relx=0.01, rely=0.01, anchor="nw")
pwc_ent.bind("<Return>", lambda _: npw_ent.focus_set() if not npw_ent.get() else npc_ent.focus_set() if not npc_ent.get() else chpw_submit())
npw_ent.bind("<Return>", lambda _: pwc_ent.focus_set() if not pwc_ent.get() else npc_ent.focus_set() if not npc_ent.get() else chpw_submit())
npc_ent.bind("<Return>", lambda _: pwc_ent.focus_set() if not pwc_ent.get() else npw_ent.focus_set() if not npw_ent.get() else chpw_submit())

delid = TkPageFrame(root)
dtitle_lbl = Label(delid, text="Delete Account", font=font.Font(size=30))
dtitle_lbl.place(relx=0.5, rely=0.25, anchor="n")
del_form = Frame(delid)
del_form.place(relx=0.5, rely=0.35, anchor="n")
username_delid = Frame(del_form)
username_delid.pack()
dun_lbl = Label(username_delid, text="Username  ", font=font.Font(size=20))
dun_lbl.pack(side="left")
dun_ent = Entry(username_delid, font=font.Font(size=20))
dun_ent.pack(side="right")
password_delid = Frame(del_form)
password_delid.pack(anchor="e")
dpw_lbl = Label(password_delid, text="Password  ", font=font.Font(size=20))
dpw_lbl.pack(side="left")
dpw_ent = Entry(password_delid, font=font.Font(size=20), show="·")
dpw_ent.pack(side="right")
dsubmit = Button(delid, text="Submit", font=font.Font(size=20), cursor="hand2", command=delid_submit)
dsubmit.place(relx=0.5, rely=0.45, anchor="n")
dback = Button(delid, image=arrow, command=mypage_page, borderwidth=0, highlightthickness=0, bd=0, relief="flat", cursor="hand2")
dback.place(relx=0.01, rely=0.01, anchor="nw")
dun_ent.bind("<Return>", lambda _: dpw_ent.focus_set() if not dpw_ent.get() else delid_submit())
dpw_ent.bind("<Return>", lambda _: dun_ent.focus_set() if not dun_ent.get() else delid_submit())

game = TkPageFrame(root)
canvas = Canvas(game)
canvas.pack(expand=True, fill="both")
lbl_txt = Label(game, text="Mode: 0", font=font.Font(size=20))
lbl_txt.pack(fill="y", pady=10)

main.pack(expand=True, fill="both")

magnet0 = (rel_width // 2 - 25, int(rel_height) - 51, rel_width // 2 + 25, int(rel_height) - 1)
magnet = magnet0
magnet_edge = (-2, 0, rel_width + 2, rel_height)
magnet_v = [0, 0]
speed_abs = 0.5
letter_cnt = 0
letter0y = (-50, 0)
letter0x = []
letter = []
letter_v = []
letters = []
letter_a = 1
magdmx = 200
grv = 0.1
atch = []
atcf = []
bomb_cnt = 0
bomb0x = []
bomb = []
bomb_v = []
newb = True
word_n = ""

space = "rel"
mode = "0"

last_time = time.time()
frames = 60
frameq = 60
time_count = 1 / frameq

while running:
    last_time = time.time()
    if playing:
        canvas.delete("all")
        win_size = (canvas.winfo_width(), canvas.winfo_height())
        if last_win_size != win_size:
            offset = offset_info()
            bg_img = crop_img(os.path.join(base_path, "img", "background.png"), offset[0][0][1], offset[1][0][1], offset[0][1][0], offset[1][1][0])
        canvas.create_image(offset[0][0][1], offset[1][0][1], anchor="nw", image=bg_img)
        dirc = [0, 0]
        speed = speed_abs
        if keyboard.is_pressed("left"):
            dirc[0] -= speed
        if keyboard.is_pressed("right"):
            dirc[0] += speed
        if keyboard.is_pressed("up"):
            dirc[1] -= speed
        if keyboard.is_pressed("down"):
            dirc[1] += speed
        if dirc[0] != 0 and dirc[1] != 0:
            dirc[0] *= math.sqrt(2) / 2
            dirc[1] *= math.sqrt(2) / 2
        magnet_v[0] += dirc[0]
        magnet_v[1] += dirc[1]
        magnet_v[0] *= 0.95
        magnet_v[1] *= 0.95
        magnet = (magnet[0] + magnet_v[0], magnet[1] + magnet_v[1], magnet[2] + magnet_v[0], magnet[3] + magnet_v[1])
        if magnet[0] < magnet_edge[0]:
            dx = magnet_edge[0] - magnet[0]
            magnet_v[0] = 0
        elif magnet[2] > magnet_edge[2]:
            dx = magnet_edge[2] - magnet[2]
            magnet_v[0] = 0
        else:
            dx = 0
        if magnet[1] < magnet_edge[1]:
            dy = magnet_edge[1] - magnet[1]
            magnet_v[1] = 0
        elif magnet[3] > magnet_edge[3]:
            dy = magnet_edge[3] - magnet[3]
            magnet_v[1] = 0
        else:
            dy = 0
        magnet = (magnet[0] + dx, magnet[1] + dy, magnet[2] + dx, magnet[3] + dy)
        magnet_abs = (*relative_to_absolute(magnet[0], magnet[1]), *relative_to_absolute(magnet[2], magnet[3]))
        if last_win_size != win_size:
            magnet_img = crop_img(os.path.join(base_path, "img", "magnet.png"), *magnet_abs)
        canvas.create_image(magnet_abs[0], magnet_abs[1], anchor="nw", image=magnet_img)
        if keyboard.is_pressed(2):
            if space == "rel":
                space = "1"
                mode = "1"
                magdmx = 100
                letter_a = -50
        elif mode == "1":
            magdmx = 150
            letter_a = 1
            mode = "0"
        if keyboard.is_pressed(3):
            if space == "rel":
                if mode != "0" and mode != "2":
                    magdmx = 150
                    letter_a = 5
                    mode = "0"
                space = "2"
                mode = "2" if mode == "0" else "0"
                magdmx = 100 if magdmx == 200 else 200
                letter_a = 15 if letter_a == 1 else 1
        if keyboard.is_pressed(4):
            if space == "rel":
                if mode != "0" and mode != "3":
                    magdmx = 150
                    letter_a = 1
                    mode = "0"
                space = "3"
                mode = "3" if mode == "0" else "0"
                magdmx = 1000 if magdmx == 200 else 200
                letter_a = 5 if letter_a == 1 else 1
        if not (keyboard.is_pressed("1") or keyboard.is_pressed("2") or keyboard.is_pressed("3")):
            space = "rel"
        if random.randint(1, 100) == 1 and letter_cnt <= 30:
            letter0x.append(random.randint(25, rel_width - 25))
            letter.append((letter0x[-1] - 25, letter0y[0], letter0x[-1] + 25, letter0y[1]))
            letter_v.append([0, 0])
            letters.append(random.choice(letter_list))
            letter_cnt += 1
        if random.randint(1, 100) == 1 and bomb_cnt <= 10:
            bomb0x.append(random.randint(25, rel_width - 25))
            bomb.append((bomb0x[-1] - 25, letter0y[0], bomb0x[-1] + 25, letter0y[1]))
            bomb_v.append([0, 0])
            bomb_cnt += 1
        dels = []
        atch = []
        atcf = []
        for i in range(letter_cnt):
            if mode == "2":
                hard = False
            atchd = False
            letter_v[i][1] += grv
            dx = ((magnet[0] + magnet[2]) / 2) - ((letter[i][0] + letter[i][2]) / 2)
            dy = magnet[1] - ((letter[i][1] + letter[i][3]) / 2)
            dy2 = ((magnet[1] + magnet[3]) / 2) - ((letter[i][1] + letter[i][3]) / 2)
            length = math.hypot(dx, dy)
            if math.hypot(dx, dy2) < magdmx / 4 and mode != "1" and mode != "3":
                ma = 1000
            else:
                ma = magdmx
            letter_magdv = letter_a * max(0, 1 - (length / ma))
            if letter_magdv > 0 and len(atch) < 5:
                atch.append(letters[i])
                atchd = True
            elif mode != "1":
                letter_magdv = 0
            k = 0.95
            if (((math.hypot(dx, dy2) < magdmx / 4 and mode != "1" and mode != "3") or \
                (mode in "23" and math.hypot(dx, dy2) < 50))) and atchd:
                letter_magdv = 0
                letter_v[i][1] -= grv
                k = 0.75
            if (((math.hypot(dx, dy2) < magdmx / 4 + 50 and mode != "1" and mode != "3") or \
                (mode in "23" and math.hypot(dx, dy2) < 100))) and atchd:
                atcf.append(letters[i])
                atchf = True
            letter_mage = [dx / length, dy / length]
            letter_magv = [letter_mage[0] * letter_magdv, letter_mage[1] * letter_magdv]
            letter_v[i][0] += letter_magv[0]
            letter_v[i][1] += letter_magv[1]
            letter_v[i][0] *= k
            letter_v[i][1] *= k
            letter[i] = (letter[i][0] + letter_v[i][0], letter[i][1] + letter_v[i][1], \
                letter[i][2] + letter_v[i][0], letter[i][3] + letter_v[i][1])
            letter_abs = (*relative_to_absolute(letter[i][0], letter[i][1]), \
                *relative_to_absolute(letter[i][2], letter[i][3]))
            if not (-100 < letter[i][1] < rel_height + 50 and -100 < letter[i][0] < rel_width + 100):
                dels.append(i)
            canvas.create_text((letter_abs[0] + letter_abs[2]) // 2, (letter_abs[1] + letter_abs[3]) // 2, \
                text=letters[i], font=font.Font(size=(letter_abs[3] - letter_abs[1]) // -2))
        rg = list(range(letter_cnt))
        for i in dels:
            j = rg.index(i)
            del letter0x[j], letter[j], letter_v[j], letters[j], rg[j]
            letter_cnt -= 1
        inc = process.calculate("".join(atcf))
        if len(inc) != 0:
            letter_cnt = 0
            letter0x = []
            letter = []
            letter_v = []
            letters = []
            atch = []
            atcf = []
            bomb_cnt = 0
            bomb0x = []
            bomb = []
            bomb_v = []
            score += process.get_diff()
            word_n = inc
        if mostsp in inc:
            main_page(True)
        dels = []
        for i in range(bomb_cnt):
            bomb_v[i][1] += grv
            dx = ((magnet[0] + magnet[2]) / 2) - ((bomb[i][0] + bomb[i][2]) / 2)
            dy = magnet[1] - ((bomb[i][1] + bomb[i][3]) / 2)
            dy2 = ((magnet[1] + magnet[3]) / 2) - ((bomb[i][1] + bomb[i][3]) / 2)
            length = math.hypot(dx, dy)
            if math.hypot(dx, dy2) < magdmx / 4 and mode != "1" and mode != "3":
                ma = 1000
            else:
                ma = magdmx
            if math.hypot(dx, dy2) < 50 and mode != "1":
                playing = False
                if score > maxscore:
                    maxscore = score
                main_page()
                win_lbl.configure(text="Magnet Crashed by Bomb")
            bomb_magdv = letter_a * max(0, 1 - (length / ma))
            bomb_mage = [dx / length, dy / length]
            bomb_magv = [bomb_mage[0] * bomb_magdv, bomb_mage[1] * bomb_magdv]
            bomb_v[i][0] += bomb_magv[0]
            bomb_v[i][1] += bomb_magv[1]
            bomb_v[i][0] *= 0.95
            bomb_v[i][1] *= 0.95
            bomb[i] = (bomb[i][0] + bomb_v[i][0], bomb[i][1] + bomb_v[i][1], \
                bomb[i][2] + bomb_v[i][0], bomb[i][3] + bomb_v[i][1])
            bomb_abs = (*relative_to_absolute(bomb[i][0], bomb[i][1]), \
                *relative_to_absolute(bomb[i][2], bomb[i][3]))
            if not (-100 < bomb[i][1] < rel_height + 50 and -100 < bomb[i][0] < rel_width + 100):
                dels.append(i)
            if last_win_size != win_size or newb:
                bomb_img = crop_img(os.path.join(base_path, "img", "bomb.png"), *bomb_abs)
                newb = False
            canvas.create_image(bomb_abs[0], bomb_abs[1], anchor="nw", image=bomb_img)
        rg = list(range(bomb_cnt))
        for i in dels:
            j = rg.index(i)
            del bomb0x[j], bomb[j], bomb_v[j], rg[j]
            bomb_cnt -= 1
        last_win_size = win_size
        lbl_txt.configure(text=f"Mode: {mode} | Letters: {", ".join(atcf)} | Score: {score} | Word: {", ".join(word_n)}")
    root.update()
    time.sleep(max(0, 1 / frameq + last_time - time.time()))
    frames =  int(1 / (time.time() - last_time))
    print(f"{frames} fps")