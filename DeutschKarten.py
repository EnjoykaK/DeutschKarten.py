import tkinter as tk
from tkinter import Tk, simpledialog
import sqlite3
from tkinter import messagebox
from PIL import Image, ImageTk
import os


window = Tk()
window.title("Deutsch-Russisch Karten")
window.configure(bg="violet")
window.geometry("500x500")

icon_path = r"C:\Users\Student\OneDrive - GFN GmbH (EDU)\Dokumente\My Python\DeutschKart\icon\deutschkarten.png"
if os.path.exists(icon_path):
    img = Image.open(icon_path)
    photo = ImageTk.PhotoImage(img)
    window.iconphoto(False, photo)



def verbinden():
   return sqlite3.connect('deutschkarten.db')

with verbinden() as conn:
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS blocks (
                   id INTEGER PRIMARY KEY,
                   name TEXT,
                   date TEXT
               );
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS cards (
                   id INTEGER PRIMARY KEY,
                   deutsch TEXT,
                   russisch TEXT,
                   block_id INTEGER
               );
                   """)
    conn.commit()

def hinzufügen():
    window.lift()
    window.focus_force()
    deutsch = simpledialog.askstring("Deutsch", "Deutsche Wort?", parent = window)
    russisch = simpledialog.askstring("Russisch", "Russische Wort?", parent = window)
    if deutsch and russisch:
        with verbinden() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cards (deutsch, russisch, block_id) VALUES (?, ?, ?);", (deutsch, russisch, 1)
            )
        conn.commit()
    messagebox.showinfo("Готово!", f"Слово '{deutsch}' добавлено!")
btn_add = tk.Button(window, text="Добавить карточку", command=hinzufügen, bg="white")
btn_add.pack(pady=20)

window.mainloop()
